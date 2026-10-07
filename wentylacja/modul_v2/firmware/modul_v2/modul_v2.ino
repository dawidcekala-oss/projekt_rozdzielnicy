/*
 * MODUŁ v2 — firmware ESP32
 *
 * Odczyt magistrali RS-485 klimatyzatora Gree GKH + sterowanie podczerwienią,
 * z weryfikacją każdej komendy przez magistralę.
 *
 * Wobec sondy v10 (ESP8266):
 *   - sprzętowy UART2 zamiast programowego  -> koniec ramek z błędną sumą,
 *   - nastawy w pamięci NVS zamiast EEPROM,
 *   - doszedł odbiornik podczerwieni: nauka kodów z pilota i kontrola echa
 *     własnego nadajnika (moduł słyszy sam siebie).
 *
 * Kontrakt sieciowy (/stan, /ustaw) jest ZGODNY z v10 — karta panelu w Home
 * Assistancie nie wymaga żadnych zmian; doszły tylko nowe pola JSON.
 *
 * Schemat i tabele połączeń: ..\..\MODUL_v2.pdf
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>
#include <Preferences.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <IRrecv.h>
#include <IRutils.h>
#include <ir_Gree.h>

// ── konfiguracja ──────────────────────────────────────────────────────────
const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";
const char* NAZWA_OTA = "modul-gree-1";        // zmienić dla każdego egzemplarza!

const uint8_t PIN_RX    = 16;   // UART2 RX  <- RO modułu MAX3485
const uint8_t PIN_TX    = 17;   // UART2 TX  -> DI modułu MAX3485
const uint8_t PIN_DIR   = 4;    // DE+RE     (nisko = odbiór)
const uint8_t PIN_IR_TX = 23;   // baza tranzystora przez 470 Ω
const uint8_t PIN_IR_RX = 19;   // wyjście VS1838B

const unsigned long ODSTEP_BEACON_MS = 2000UL;
const int  OFFSET_TEMP   = 100;         // bajt magistrali − 100 = °C
const uint16_t PORT_HTTP = 80;

// ── obiekty ───────────────────────────────────────────────────────────────
HardwareSerial magistrala(2);
WebServer   http(PORT_HTTP);
WiFiServer  telnet(23);
WiFiClient  klient;
WiFiUDP     udp;
Preferences nvs;

IRGreeAC klima(PIN_IR_TX);
IRrecv   odbiornik(PIN_IR_RX, 1024, 90, true);
decode_results wynikIR;

// ── stan jednostki (z rozgłoszenia FF->40) ────────────────────────────────
struct Stan {
  bool     jest          = false;
  int      tempPokoj     = 0;
  int      tempWymiennik = 0;
  uint8_t  bieg          = 0;
  bool     klapy         = false;
  unsigned long ostatniaMs = 0;
  uint32_t ramekOK       = 0;
  uint32_t ramekZlaSuma  = 0;
} stan;

// ── nastawy zadane (pamiętane w NVS) ──────────────────────────────────────
struct Zadane {
  bool     wl    = false;
  uint8_t  temp  = 22;
  uint8_t  tryb  = kGreeCool;
  uint8_t  went  = kGreeFanAuto;
  bool     swing = false;
  uint8_t  model = 1;                  // 1=YAW1F 2=YBOFB 3=YX1FSF
  uint32_t wyslanych = 0;
} zad;

// ── weryfikacja komendy przez magistralę ──────────────────────────────────
const unsigned long OKNO_WERYF_MS = 14000UL;
const uint8_t MAX_PONOWIEN = 2;
const uint8_t POWTORZEN_IR = 3;

unsigned long weryfDo           = 0;
uint8_t       ponowien          = 0;
int8_t        potwierdzone      = -1;   // -1 nieznane, 0 nie, 1 tak
unsigned long ostatniaKomendaMs = 0;

// ── nauka i echo podczerwieni ─────────────────────────────────────────────
String   ostatniKodIR   = "";
String   ostatniProtIR  = "";
int8_t   echoIR         = -1;           // -1 nie badano, 0 nie słychać, 1 słychać
unsigned long naukaDo   = 0;            // tryb nauki: nasłuch pilota

// ── bufory i pomocnicze ───────────────────────────────────────────────────
uint8_t  buf[64];
uint8_t  bufLen = 0;
String   ring;
const unsigned int RING_MAX = 1500;
String   liniaCmd;
bool     wifiBylo = false;
unsigned long startMs = 0, ostatniBeacon = 0, ostatniBajtMs = 0;
unsigned long ostatniaKontrolaPam = 0;
uint32_t minWolnejPamieci = 0xFFFFFFFF;

void emit(const String& s) {
  Serial.print(s);
  if (klient && klient.connected()) klient.print(s);
  ring += s;
  if (ring.length() > RING_MAX) ring = ring.substring(ring.length() - RING_MAX);
}

String hex2(uint8_t b) {
  const char* z = "0123456789ABCDEF";
  return String(z[b >> 4]) + String(z[b & 0x0F]);
}

const char* nazwaBiegu(uint8_t b) {
  switch (b) {
    case 0x00: return "stoi";
    case 0x04: return "niski";
    case 0x02: return "sredni";
    case 0x01: return "wysoki";
    default:   return "?";
  }
}
const char* nazwaTrybu(uint8_t m) {
  switch (m) {
    case kGreeAuto: return "auto";
    case kGreeCool: return "chlodzenie";
    case kGreeDry:  return "osuszanie";
    case kGreeFan:  return "wentylacja";
    case kGreeHeat: return "grzanie";
    default:        return "?";
  }
}
const char* nazwaWent(uint8_t f) {
  switch (f) {
    case kGreeFanAuto: return "auto";
    case kGreeFanMin:  return "niski";
    case kGreeFanMed:  return "sredni";
    case kGreeFanMax:  return "wysoki";
    default:           return "?";
  }
}

// ── nastawy w pamięci nieulotnej ──────────────────────────────────────────
void zapiszNastawy() {
  nvs.begin("modul", false);
  nvs.putBool("wl", zad.wl);
  nvs.putUChar("temp", zad.temp);
  nvs.putUChar("tryb", zad.tryb);
  nvs.putUChar("went", zad.went);
  nvs.putBool("swing", zad.swing);
  nvs.putUChar("model", zad.model);
  nvs.end();
}

bool czytajNastawy() {
  nvs.begin("modul", true);
  bool jest = nvs.isKey("temp");
  if (jest) {
    zad.wl    = nvs.getBool("wl", false);
    zad.temp  = nvs.getUChar("temp", 22);
    zad.tryb  = nvs.getUChar("tryb", kGreeCool);
    zad.went  = nvs.getUChar("went", kGreeFanAuto);
    zad.swing = nvs.getBool("swing", false);
    zad.model = nvs.getUChar("model", 1);
  }
  nvs.end();
  if (zad.temp < 16 || zad.temp > 30) zad.temp = 22;
  if (zad.model < 1 || zad.model > 3) zad.model = 1;
  return jest;
}

// ── odbiór magistrali ─────────────────────────────────────────────────────
// Jednostka rozgłasza 29-bajtową ramkę do adresu 0x40 równo co 800 ms.
// Nie odpowiada na nic — nasza rola to bierny podsłuch.
void analizujBufor() {
  if (bufLen < 29) return;
  for (int i = 0; i + 29 <= bufLen; i++) {
    if (buf[i] != 0x7E || buf[i + 1] != 0x7E) continue;
    uint8_t* r = buf + i;
    uint8_t x = 0;
    for (int k = 0; k < 28; k++) x ^= r[k];
    if (x != r[28]) { stan.ramekZlaSuma++; continue; }

    stan.jest          = true;
    stan.tempPokoj     = (int)r[9]  - OFFSET_TEMP;
    stan.tempWymiennik = (int)r[10] - OFFSET_TEMP;
    stan.bieg          = r[12];
    stan.klapy         = (r[14] == 0x80);
    stan.ostatniaMs    = millis();
    stan.ramekOK++;

    memmove(buf, r + 29, bufLen - i - 29);
    bufLen -= (i + 29);
    return;
  }
  if (bufLen > 48) { memmove(buf, buf + bufLen - 32, 32); bufLen = 32; }
}

void odbieraj() {
  while (magistrala.available()) {
    uint8_t b = magistrala.read();
    ostatniBajtMs = millis();
    if (bufLen < sizeof(buf)) buf[bufLen++] = b;
    else { memmove(buf, buf + 1, sizeof(buf) - 1); buf[sizeof(buf) - 1] = b; }
    analizujBufor();
  }
}

// ── podczerwień: nadawanie ────────────────────────────────────────────────
void ustawRamke() {
  switch (zad.model) {
    case 2:  klima.setModel(gree_ac_remote_model_t::YBOFB); break;
    case 3:  klima.setModel(gree_ac_remote_model_t::YX1FSF); break;
    default: klima.setModel(gree_ac_remote_model_t::YAW1F); break;
  }
  klima.setPower(zad.wl);
  klima.setTemp(zad.temp);
  klima.setMode(zad.tryb);
  klima.setFan(zad.went);
  klima.setSwingVertical(zad.swing, zad.swing ? kGreeSwingAuto : kGreeSwingLastPos);
  klima.setLight(true);
}

// Nadaje ramkę i sprawdza, czy własny odbiornik ją usłyszał.
// To jest test nadajnika NIEZALEŻNY od klimatyzatora: jeśli echo milczy,
// wina leży w torze diody, a nie w celowaniu czy w jednostce.
void wyslijIR() {
  ustawRamke();
  odbiornik.resume();
  for (uint8_t i = 0; i < POWTORZEN_IR; i++) {
    klima.send();
    zad.wyslanych++;
    if (i + 1 < POWTORZEN_IR) delay(45);
  }
  echoIR = 0;
  unsigned long doKiedy = millis() + 250;
  while (millis() < doKiedy) {
    if (odbiornik.decode(&wynikIR)) {
      if (wynikIR.decode_type == decode_type_t::GREE) echoIR = 1;
      odbiornik.resume();
      if (echoIR == 1) break;
    }
    delay(5);
  }
  emit("[IR] wyslano x" + String(POWTORZEN_IR) + ": wl=" + String(zad.wl) +
       " temp=" + String(zad.temp) + " tryb=" + nazwaTrybu(zad.tryb) +
       " went=" + nazwaWent(zad.went) +
       " | echo wlasnego nadajnika: " + String(echoIR == 1 ? "SLYCHAC" : "cisza") + "\n");
}

// Bieg zadany (kodowanie pilota) -> kod biegu widziany na magistrali.
int oczekiwanyBieg() {
  if (!zad.wl) return 0;
  if (zad.went == kGreeFanMin) return 4;
  if (zad.went == kGreeFanMed) return 2;
  if (zad.went == kGreeFanMax) return 1;
  return -1;                                   // auto — jednostka wybiera sama
}

bool zgodneZZadanym() {
  if (!stan.jest) return false;
  if (millis() - stan.ostatniaMs > 10000UL) return false;
  if ((stan.bieg != 0) != zad.wl) return false;
  if (zad.tryb == kGreeCool || zad.tryb == kGreeFan || zad.tryb == kGreeHeat) {
    int ocz = oczekiwanyBieg();
    if (ocz > 0 && stan.bieg != (uint8_t)ocz) return false;
  }
  return true;
}

void zadajKomende() {
  wyslijIR();
  ostatniaKomendaMs = millis();
  ponowien     = 0;
  potwierdzone = -1;
  weryfDo      = millis() + OKNO_WERYF_MS;
  zapiszNastawy();
}

void obsluzWeryfikacje() {
  if (weryfDo == 0 || millis() < weryfDo) return;
  if (zgodneZZadanym()) {
    weryfDo = 0; potwierdzone = 1; ponowien = 0;
    emit("[IR] POTWIERDZONE przez magistrale\n");
    return;
  }
  if (ponowien < MAX_PONOWIEN) {
    ponowien++;
    emit("[IR] brak potwierdzenia — ponowienie " + String(ponowien) +
         "/" + String(MAX_PONOWIEN) + "\n");
    wyslijIR();
    weryfDo = millis() + OKNO_WERYF_MS;
  } else {
    weryfDo = 0; potwierdzone = 0;
    emit("[IR] NIEPOTWIERDZONE — sprawdz diode przy odbiorniku jednostki\n");
  }
}

// ── podczerwień: nauka z pilota ───────────────────────────────────────────
void obsluzNauke() {
  if (!odbiornik.decode(&wynikIR)) return;
  ostatniProtIR = typeToString(wynikIR.decode_type);
  ostatniKodIR  = resultToHexidecimal(&wynikIR);
  emit("[IR] odebrano: " + ostatniProtIR + " / " + ostatniKodIR +
       " (" + String(wynikIR.bits) + " bitow)\n");
  odbiornik.resume();
}

// ── HTTP ──────────────────────────────────────────────────────────────────
void httpStan() {
  unsigned long wiek = stan.jest ? (millis() - stan.ostatniaMs) : 0;
  bool swieze = stan.jest && wiek < 10000;
  String j = "{";
  j += "\"dostepne\":" + String(swieze ? "true" : "false");
  j += ",\"temp_pokoj\":" + String(stan.tempPokoj);
  j += ",\"temp_wymiennik\":" + String(stan.tempWymiennik);
  j += ",\"wentylator\":\"" + String(nazwaBiegu(stan.bieg)) + "\"";
  j += ",\"wentylator_kod\":" + String(stan.bieg);
  j += ",\"pracuje\":" + String(stan.bieg != 0 ? "true" : "false");
  j += ",\"klapy_otwarte\":" + String(stan.klapy ? "true" : "false");
  j += ",\"wiek_danych_ms\":" + String(wiek);
  j += ",\"ramek_ok\":" + String(stan.ramekOK);
  j += ",\"ramek_zla_suma\":" + String(stan.ramekZlaSuma);
  j += ",\"cisza_na_magistrali_s\":" + String((millis() - ostatniBajtMs) / 1000);
  j += ",\"zad_wl\":" + String(zad.wl ? "true" : "false");
  j += ",\"zad_temp\":" + String(zad.temp);
  j += ",\"zad_tryb\":\"" + String(nazwaTrybu(zad.tryb)) + "\"";
  j += ",\"zad_went\":\"" + String(nazwaWent(zad.went)) + "\"";
  j += ",\"zad_swing\":" + String(zad.swing ? "true" : "false");
  j += ",\"ir_model\":" + String(zad.model);
  j += ",\"ir_wyslanych\":" + String(zad.wyslanych);
  j += ",\"potwierdzenie\":\"" + String(weryfDo != 0 ? "w_toku" :
        (potwierdzone == 1 ? "tak" : (potwierdzone == 0 ? "nie" : "brak"))) + "\"";
  j += ",\"ponowien\":" + String(ponowien);
  j += ",\"od_komendy_s\":" + String(ostatniaKomendaMs ? (millis() - ostatniaKomendaMs) / 1000 : 0);
  // nowe w v2:
  j += ",\"ir_echo\":\"" + String(echoIR == 1 ? "slychac" : (echoIR == 0 ? "cisza" : "brak")) + "\"";
  j += ",\"ir_ostatni_protokol\":\"" + ostatniProtIR + "\"";
  j += ",\"ir_ostatni_kod\":\"" + ostatniKodIR + "\"";
  j += ",\"modul\":\"" + String(NAZWA_OTA) + "\"";
  j += ",\"wolna_pamiec\":" + String(ESP.getFreeHeap());
  j += ",\"min_wolna_pamiec\":" + String(minWolnejPamieci);
  j += ",\"uptime_s\":" + String(millis() / 1000);
  j += "}";
  http.send(200, "application/json", j);
}

void httpUstaw() {
  bool zmiana = false;
  if (http.hasArg("wl"))   { zad.wl = (http.arg("wl") == "1" || http.arg("wl") == "true"); zmiana = true; }
  if (http.hasArg("temp")) { int v = http.arg("temp").toInt(); if (v >= 16 && v <= 30) { zad.temp = v; zmiana = true; } }
  if (http.hasArg("tryb")) { String m = http.arg("tryb");
      if (m == "auto") zad.tryb = kGreeAuto; else if (m == "cool") zad.tryb = kGreeCool;
      else if (m == "dry") zad.tryb = kGreeDry; else if (m == "fan") zad.tryb = kGreeFan;
      else if (m == "heat") zad.tryb = kGreeHeat;
      zmiana = true; }
  if (http.hasArg("went")) { String f = http.arg("went");
      if (f == "auto") zad.went = kGreeFanAuto; else if (f == "1") zad.went = kGreeFanMin;
      else if (f == "2") zad.went = kGreeFanMed; else if (f == "3") zad.went = kGreeFanMax;
      zmiana = true; }
  if (http.hasArg("swing")) { zad.swing = (http.arg("swing") == "1"); zmiana = true; }
  if (http.hasArg("model")) { int v = http.arg("model").toInt(); if (v >= 1 && v <= 3) zad.model = v; }
  if (zmiana || http.hasArg("send")) zadajKomende();
  httpStan();
}

void httpStrona() {
  String h = "<meta charset=\"utf-8\"><title>Modul v2</title><h2>Modul v2 — ";
  h += String(NAZWA_OTA) + "</h2><pre>";
  h += "temperatura pomieszczenia : " + String(stan.tempPokoj) + " C\n";
  h += "temperatura wymiennika    : " + String(stan.tempWymiennik) + " C\n";
  h += "wentylator                : " + String(nazwaBiegu(stan.bieg)) + "\n";
  h += "klapy                     : " + String(stan.klapy ? "otwarte" : "zamkniete") + "\n\n";
  h += "ramek poprawnych          : " + String(stan.ramekOK) + "\n";
  h += "ramek z bledna suma       : " + String(stan.ramekZlaSuma) + "\n";
  h += "cisza na magistrali       : " + String((millis() - ostatniBajtMs) / 1000) + " s\n\n";
  h += "nastawa                   : " + String(zad.temp) + " C, " + nazwaTrybu(zad.tryb) +
       ", bieg " + nazwaWent(zad.went) + (zad.wl ? ", wlaczony" : ", wylaczony") + "\n";
  h += "echo nadajnika IR         : " + String(echoIR == 1 ? "slychac" : (echoIR == 0 ? "CISZA" : "nie badano")) + "\n";
  h += "ostatni kod z pilota      : " + ostatniProtIR + " / " + ostatniKodIR + "\n";
  h += "uptime                    : " + String(millis() / 1000) + " s\n";
  h += "</pre><p><a href=\"/stan\">/stan</a> — dane dla Home Assistanta</p>";
  http.send(200, "text/html", h);
}

// ── komendy telnet ────────────────────────────────────────────────────────
void obsluzKomende(String l) {
  l.trim();
  String D = l; D.toUpperCase();
  if (!D.length()) return;

  if (D == "INFO") {
    emit("[INFO] " + String(NAZWA_OTA) + " | IP " + WiFi.localIP().toString() +
         " | uptime " + String(millis() / 1000) + " s | pamiec " + String(ESP.getFreeHeap()) + " B\n");
    emit("[INFO] ramek OK " + String(stan.ramekOK) + ", blednych " + String(stan.ramekZlaSuma) + "\n");
    return;
  }
  if (D == "RESET") { emit("[CMD] restart\n"); delay(200); ESP.restart(); }
  if (D == "IR ON")  { zad.wl = true;  zadajKomende(); return; }
  if (D == "IR OFF") { zad.wl = false; zadajKomende(); return; }
  if (D == "IR SEND"){ zadajKomende(); return; }
  if (D.startsWith("IR TEMP ")) {
    int v = D.substring(8).toInt();
    if (v >= 16 && v <= 30) { zad.temp = v; zadajKomende(); }
    else emit("[IR] temp 16..30\n");
    return;
  }
  if (D.startsWith("IR TRYB ")) {
    String a = D.substring(8);
    if (a == "COOL") zad.tryb = kGreeCool; else if (a == "HEAT") zad.tryb = kGreeHeat;
    else if (a == "DRY") zad.tryb = kGreeDry; else if (a == "FAN") zad.tryb = kGreeFan;
    else if (a == "AUTO") zad.tryb = kGreeAuto; else { emit("[IR] tryb: cool/heat/dry/fan/auto\n"); return; }
    zadajKomende(); return;
  }
  if (D.startsWith("IR WENT ")) {
    String a = D.substring(8);
    if (a == "AUTO") zad.went = kGreeFanAuto; else if (a == "1") zad.went = kGreeFanMin;
    else if (a == "2") zad.went = kGreeFanMed; else if (a == "3") zad.went = kGreeFanMax;
    else { emit("[IR] went: auto/1/2/3\n"); return; }
    zadajKomende(); return;
  }
  if (D == "NAUKA") {
    naukaDo = millis() + 60000UL;
    ostatniKodIR = ""; ostatniProtIR = "";
    emit("[IR] tryb nauki na 60 s — nacisnij przycisk pilota celujac w odbiornik modulu\n");
    return;
  }
  emit("[CMD] nieznane. Dostepne: INFO, RESET, NAUKA, IR ON/OFF/SEND, IR TEMP n, IR TRYB x, IR WENT x\n");
}

// ── start ─────────────────────────────────────────────────────────────────
void setup() {
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);           // domyślnie odbiór — na magistralę nie nadajemy
  Serial.begin(115200);

  magistrala.begin(1200, SERIAL_8N1, PIN_RX, PIN_TX);

  bool wczytane = czytajNastawy();

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                 // stabilniejszy odbiór przy ciągłym nasłuchu
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  telnet.begin();

  http.on("/stan", httpStan);
  http.on("/ustaw", httpUstaw);
  http.on("/", httpStrona);
  http.begin();

  klima.begin();
  odbiornik.enableIRIn();

  ArduinoOTA.setHostname(NAZWA_OTA);
  ArduinoOTA.begin();

  startMs = millis();
  ostatniBajtMs = millis();
  emit("\n=== MODUL v2 (" + String(NAZWA_OTA) + ") — ESP32, UART2 sprzetowy ===\n");
  emit(wczytane ? "[NASTAWY] wczytane z pamieci\n" : "[NASTAWY] pamiec pusta — wartosci domyslne\n");
}

// ── pętla główna: nic jej nie blokuje ─────────────────────────────────────
void loop() {
  ArduinoOTA.handle();
  http.handleClient();

  odbieraj();
  obsluzWeryfikacje();

  if (naukaDo > millis()) obsluzNauke();
  else if (naukaDo != 0) { naukaDo = 0; emit("[IR] koniec trybu nauki\n"); }

  // strażnik pamięci: restart zamiast cichego zawieszenia
  if (millis() - ostatniaKontrolaPam > 5000) {
    ostatniaKontrolaPam = millis();
    uint32_t wolna = ESP.getFreeHeap();
    if (wolna < minWolnejPamieci) minWolnejPamieci = wolna;
    if (wolna < 20000) {
      emit("[STRAZNIK] pamiec " + String(wolna) + " B — restart\n");
      delay(300);
      ESP.restart();
    }
    if (wolna < 40000 && ring.length() > 800) ring = ring.substring(ring.length() - 800);
  }

  if (WiFi.status() == WL_CONNECTED && !wifiBylo) {
    wifiBylo = true;
    emit("[WiFi] POLACZONO, IP: " + WiFi.localIP().toString() + "\n");
  } else if (WiFi.status() != WL_CONNECTED && wifiBylo) {
    wifiBylo = false;
    emit("[WiFi] utracono polaczenie\n");
  }

  if (wifiBylo && millis() - ostatniBeacon > ODSTEP_BEACON_MS) {
    ostatniBeacon = millis();
    IPAddress ip = WiFi.localIP(), m = WiFi.subnetMask(), b;
    for (int i = 0; i < 4; i++) b[i] = ip[i] | ~m[i];
    udp.beginPacket(b, 4210);
    udp.print("MODUL-GREE " + String(NAZWA_OTA) + " " + ip.toString());
    udp.endPacket();
  }

  if (telnet.hasClient()) {
    if (klient) klient.stop();
    klient = telnet.accept();
    liniaCmd = "";
    klient.print("=== MODUL v2 (" + String(NAZWA_OTA) + ") ===\n--- HISTORIA ---\n");
    klient.print(ring);
    klient.print("\n--- NA ZYWO ---\n");
  }

  while (klient && klient.connected() && klient.available()) {
    char c = klient.read();
    if (c == '\n') { obsluzKomende(liniaCmd); liniaCmd = ""; }
    else if (c != '\r' && liniaCmd.length() < 200) liniaCmd += c;
  }
}
