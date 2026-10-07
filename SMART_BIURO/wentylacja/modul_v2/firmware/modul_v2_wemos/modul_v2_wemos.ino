/*
 * MODUŁ v2 — firmware dla WeMos D1 R1 (ESP8266)
 *
 * Wersja zapasowa modułu v2 na procesorze z dawnej sondy v10. Robi to samo, co
 * wersja na ESP32, i wystawia ten sam kontrakt sieciowy (`/stan`, `/ustaw`),
 * więc Home Assistant nie wymaga żadnych zmian poza adresem modułu.
 *
 * Nazwy gniazd na listwie WeMosa są w komentarzach podane tak, jak są
 * nadrukowane na płytce — jedno gniazdo nosi po kilka nazw naraz.
 *
 * Czym ta wersja różni się od wersji na ESP32 i dlaczego:
 *
 *  1. Magistralę czyta SPRZĘTOWY port szeregowy UART0, przeniesiony programowo
 *     na gniazdo "D11/MOSI/D7" (`Serial.swap()`) i odwracający sygnał w samym
 *     układzie (`invert = true`). Gree trzyma linię w spoczynku nisko, więc bez
 *     odwrócenia port nie złapałby ani jednego bajtu.
 *     Miękkiego odbiornika z ESP32 (przerwanie co 52 µs) NIE wolno tu powtarzać:
 *     to właśnie próbkowanie programowe wywracało sondę v10 przy obciążeniu WiFi
 *     i było powodem przejścia na ESP32 (MODUL_v2.pdf, rozdz. 7.1).
 *
 *  2. Nastawy leżą w EEPROM (emulowanym we flashu), bo ESP8266 nie ma NVS.
 *
 *  3. ESP8266 nie ma czujnika temperatury rdzenia → pole `temp_procesora_c`
 *     w `/stan` jest puste (null). Porównanie temperatur między modułami
 *     działa tylko na egzemplarzach z ESP32.
 *
 *  4. GPIO w ESP8266 nie mają podciągania w dół, więc test pinu (`/pin`)
 *     sprawdza tylko podciąganie w górę.
 *
 *  5. Strażnik zawieszenia jest wbudowany w SDK (programowy, ok. 3,2 s), więc
 *     nie trzeba go zakładać ręcznie. Za to każda pętla diagnostyczna dłuższa
 *     niż 2 s musi go karmić (`ESP.wdtFeed()`), inaczej sama wywoła restart.
 *
 *  6. Na magistralę nic nie nadajemy i nie ma przewodu do pola EN modułu RS485
 *     (jest on na stałe zwarty do masy na samym module). Dlatego nie ma tu
 *     punktów `/echo`, `/nadawaj`, `/kierunek` ani testu pętli zwrotnej.
 *
 * Tabela połączeń: ..\..\MODUL_WEMOS.pdf
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <EEPROM.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ir_Gree.h>

// ── konfiguracja ──────────────────────────────────────────────────────────
const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";

// Ten firmware powstał dla modułu „hala północ" (modul-gree-2). Dla innego
// egzemplarza kompilować z:
//   --build-property "compiler.cpp.extra_flags=-DMODUL_NR=4"
#ifndef MODUL_NR
#define MODUL_NR 2
#endif
#define MODUL_STR_(x) #x
#define MODUL_STR(x) MODUL_STR_(x)
const char* NAZWA_OTA = "modul-gree-" MODUL_STR(MODUL_NR);

// Piny procesora. W nawiasach opis wydrukowany na listwie WeMosa D1 R1.
const uint8_t PIN_RX    = 13;   // gniazdo "D11/MOSI/D7" <- pole TXD modułu RS485
const uint8_t PIN_IR_TX = 12;   // gniazdo "D12/MISO/D6" -> 470 Ω -> baza tranzystora
const uint8_t PIN_LED   = 2;    // niebieska dioda na srebrnym module; świeci stanem NISKIM

const unsigned long ODSTEP_BEACON_MS = 2000UL;
const int      OFFSET_TEMP = 100;       // bajt magistrali − 100 = °C
const uint16_t PORT_HTTP   = 80;
const uint16_t PORT_OTA    = 8266;      // domyślny port OTA ESP8266 (w ESP32 było 3232)

// ── obiekty ───────────────────────────────────────────────────────────────
HardwareSerial&   magistrala = Serial;  // UART0, po przeniesieniu na "D11/MOSI/D7"
ESP8266WebServer  http(PORT_HTTP);
WiFiServer        telnet(23);
WiFiClient        klient;
WiFiUDP           udp;

IRGreeAC klima(PIN_IR_TX);

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

// ── nastawy zadane (pamiętane w EEPROM) ───────────────────────────────────
struct Zadane {
  bool     wl    = false;
  uint8_t  temp  = 22;
  uint8_t  tryb  = kGreeCool;
  uint8_t  went  = kGreeFanAuto;
  bool     swing = false;
  uint8_t  model = 1;                  // 1=YAW1F 2=YBOFB 3=YX1FSF
  uint32_t wyslanych = 0;
} zad;

struct Pamiec {
  uint32_t magia;
  uint8_t  wl, temp, tryb, went, swing, model;
};
const uint32_t MAGIA = 0x47524545UL;   // "GREE"

bool nastawyZPamieci = false;
bool zamiarPrzejety  = false;
void przejmijZamiar();

// ── weryfikacja komendy przez magistralę ──────────────────────────────────
const unsigned long OKNO_WERYF_MS = 14000UL;
const uint8_t MAX_PONOWIEN = 2;
const uint8_t POWTORZEN_IR = 3;

unsigned long weryfDo           = 0;
uint8_t       ponowien          = 0;
int8_t        potwierdzone      = -1;   // -1 nieznane, 0 nie, 1 tak
unsigned long ostatniaKomendaMs = 0;

// ── bufory i pomocnicze ───────────────────────────────────────────────────
uint8_t  buf[64];
uint8_t  bufLen = 0;
String   ring;
const unsigned int RING_MAX = 1200;
String   liniaCmd;
bool     wifiBylo = false;
bool     konsolaUSB = true;             // dopóki UART0 nie należy do magistrali
uint8_t  mkOdwroc = 1;                  // 1 = sygnał odwracany w układzie UART
uint32_t mkBajty = 0, mkBledyRamki = 0, mkPrzepelnien = 0;
unsigned long startMs = 0, ostatniBeacon = 0, ostatniBajtMs = 0;
unsigned long ostatniaKontrolaPam = 0;
uint32_t minWolnejPamieci = 0xFFFFFFFF;

void emit(const String& s) {
  if (konsolaUSB) Serial.print(s);
  if (klient && klient.connected()) klient.print(s);
  ring += s;
  if (ring.length() > RING_MAX) ring = ring.substring(ring.length() - RING_MAX);
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
  Pamiec p;
  p.magia = MAGIA;
  p.wl    = zad.wl ? 1 : 0;
  p.temp  = zad.temp;
  p.tryb  = zad.tryb;
  p.went  = zad.went;
  p.swing = zad.swing ? 1 : 0;
  p.model = zad.model;
  EEPROM.put(0, p);
  EEPROM.commit();
}

bool czytajNastawy() {
  Pamiec p;
  EEPROM.get(0, p);
  bool jest = (p.magia == MAGIA);
  nastawyZPamieci = jest;
  if (jest) {
    zad.wl    = p.wl != 0;
    zad.temp  = p.temp;
    zad.tryb  = p.tryb;
    zad.went  = p.went;
    zad.swing = p.swing != 0;
    zad.model = p.model;
  }
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
    przejmijZamiar();

    memmove(buf, r + 29, bufLen - i - 29);
    bufLen -= (i + 29);
    return;
  }
  if (bufLen > 48) { memmove(buf, buf + bufLen - 32, 32); bufLen = 32; }
}

// Po pustej pamięci domyślny zamiar to „wyłączony" — wtedy każda częściowa komenda
// (sam bieg, sama temperatura) gasiłaby jednostkę. Dlatego zamiar przejmujemy
// z pierwszej poprawnej ramki magistrali: włączony <=> wentylator != 0.
void przejmijZamiar() {
  if (zamiarPrzejety || nastawyZPamieci || !stan.jest) return;
  zad.wl = (stan.bieg != 0);
  if      (stan.bieg == 0x04) zad.went = kGreeFanMin;
  else if (stan.bieg == 0x02) zad.went = kGreeFanMed;
  else if (stan.bieg == 0x01) zad.went = kGreeFanMax;
  zamiarPrzejety = true;
  emit(String("[NASTAWY] zamiar przejety z magistrali: ") + (zad.wl ? "wlaczony" : "wylaczony") +
       ", bieg " + nazwaWent(zad.went) + "\n");
}

// UART0 przeniesiony na gniazdo "D11/MOSI/D7", tylko odbiór, sygnał odwrócony.
// Po każdej diagnostyce, która zabiera ten pin, trzeba wywołać to ponownie.
void uruchomOdbiornik(bool glosno) {
  if (glosno) emit(String("[UART] magistrala: gniazdo D11/MOSI/D7, 1200 8N1, sygnal ") +
                   (mkOdwroc ? "ODWROCONY" : "wprost") + "\n");
  konsolaUSB = false;                 // od tej chwili UART0 należy do magistrali
  Serial.flush();
  Serial.end();
  Serial.setRxBufferSize(256);
  Serial.begin(1200, SERIAL_8N1, SERIAL_RX_ONLY, 1, mkOdwroc != 0);
  Serial.swap();                      // UART0 RX: gniazdo "RX<-D0" -> "D11/MOSI/D7"
}

void zwolnijPinRx() {                 // oddaje pin diagnostyce
  Serial.end();
  pinMode(PIN_RX, INPUT);
}

void odbieraj() {
  while (magistrala.available()) {
    uint8_t b = (uint8_t)magistrala.read();
    mkBajty++;
    ostatniBajtMs = millis();
    if (bufLen < sizeof(buf)) buf[bufLen++] = b;
    else { memmove(buf, buf + 1, sizeof(buf) - 1); buf[sizeof(buf) - 1] = b; }
    analizujBufor();
  }
  if (magistrala.hasRxError())  mkBledyRamki++;
  if (magistrala.hasOverrun())  mkPrzepelnien++;
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

// Nadaje ramkę POWTORZEN_IR razy. Czy jednostka ją przyjęła, rozstrzyga
// dopiero porównanie ze stanem z magistrali w obsluzWeryfikacje().
void wyslijIR() {
  ustawRamke();
  for (uint8_t i = 0; i < POWTORZEN_IR; i++) {
    klima.send();
    zad.wyslanych++;
    if (i + 1 < POWTORZEN_IR) delay(45);
  }
  emit("[IR] wyslano x" + String(POWTORZEN_IR) + ": wl=" + String(zad.wl) +
       " temp=" + String(zad.temp) + " tryb=" + nazwaTrybu(zad.tryb) +
       " went=" + nazwaWent(zad.went) + "\n");
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

// ── HTTP ──────────────────────────────────────────────────────────────────
// Surowy stan linii, którą moduł RS485 podaje procesorowi. Rozstrzyga, czy do
// modułu w ogóle dociera sygnał, bez wchodzenia na drabinę z oscyloskopem.
// Pętla karmi strażnika SDK, inaczej po 3,2 s sama wywołałaby restart.
void httpLinia() {
  bool pod = http.hasArg("pullup");
  zwolnijPinRx();
  pinMode(PIN_RX, pod ? INPUT_PULLUP : INPUT);
  uint32_t zmian = 0, wysokich = 0, probek = 0;
  int poprz = digitalRead(PIN_RX);
  unsigned long doKiedy = millis() + 3000, karma = millis();
  while (millis() < doKiedy) {
    int teraz = digitalRead(PIN_RX);
    if (teraz != poprz) { zmian++; poprz = teraz; }
    if (teraz) wysokich++;
    probek++;
    if (millis() - karma > 300) { karma = millis(); ESP.wdtFeed(); }
  }
  uruchomOdbiornik(false);
  String j = "{\"zmian\":" + String(zmian) +
             ",\"procent_wysoko\":" + String((100.0 * wysokich) / probek, 1) +
             ",\"probek\":" + String(probek) + ",\"podciagniecie\":" + String(pod ? 1 : 0) + "}";
  http.send(200, "application/json", j);
}

// ESP8266 nie ma podciągania w dół, więc test jest jednostronny: jeśli pin
// pozostaje niski mimo podciągnięcia w górę, to coś go trzyma — wyjście
// odbiornika modułu RS485 albo zwarcie do masy.
void httpPin() {
  zwolnijPinRx();
  pinMode(PIN_RX, INPUT_PULLUP);
  delay(3);
  int zPod = digitalRead(PIN_RX);
  pinMode(PIN_RX, INPUT);
  delay(3);
  int bezPod = digitalRead(PIN_RX);
  uruchomOdbiornik(false);
  String w = "gniazdo D11/MOSI/D7 (magistrala): z podciagnieciem=" + String(zPod) +
             ", bez podciagniecia=" + String(bezPod) + "  => ";
  if (zPod == 0) w += "COS TRZYMA LINIE NISKO (wyjscie odbiornika modulu albo zwarcie do masy)";
  else if (bezPod == 1) w += "linia wysoko (odbiornik trzyma wysoko albo pin wisi)";
  else w += "pin podaza za podciagnieciem — WOLNY, nic go nie steruje";
  http.send(200, "text/plain", w);
}

void httpZrzut() {
  String h = "";
  uint16_t n = 0;
  unsigned long doKiedy = millis() + 4000;
  while (millis() < doKiedy && n < 220) {
    while (magistrala.available() && n < 220) {
      uint8_t b = (uint8_t)magistrala.read();
      mkBajty++;
      ostatniBajtMs = millis();
      if (b < 16) h += "0";
      h += String(b, HEX);
      h += " ";
      n++;
    }
    delay(2);
  }
  http.send(200, "text/plain", String("odebrano ") + n + " bajtow w 4 s: " + h);
}

// Procesor sam mierzy szerokość najkrótszego impulsu na linii odbiorczej.
// Z niej wynika wprost prędkość transmisji magistrali (przy 1200 bd bit trwa 833 µs).
void httpBity() {
  zwolnijPinRx();
  pinMode(PIN_RX, INPUT);
  uint32_t min50 = 0xFFFFFFFF, min100 = 0xFFFFFFFF, min300 = 0xFFFFFFFF;
  uint32_t n = 0, ponad100 = 0, ponad300 = 0, ponad700 = 0;
  int poprz = digitalRead(PIN_RX);
  uint32_t tPoprz = micros();
  unsigned long koniec = millis() + 4000, karma = millis();
  while (millis() < koniec) {
    int teraz = digitalRead(PIN_RX);
    if (teraz != poprz) {
      uint32_t t = micros();
      uint32_t d = t - tPoprz;
      n++;
      if (d > 50  && d < min50)  min50  = d;
      if (d > 100) { ponad100++; if (d < min100) min100 = d; }
      if (d > 300) { ponad300++; if (d < min300) min300 = d; }
      if (d > 700) ponad700++;
      tPoprz = t;
      poprz = teraz;
    }
    if (millis() - karma > 300) { karma = millis(); ESP.wdtFeed(); }
  }
  uruchomOdbiornik(false);
  String w = "przelaczen: " + String(n);
  w += " | powyzej 100us: " + String(ponad100);
  w += " | powyzej 300us: " + String(ponad300);
  w += " | powyzej 700us: " + String(ponad700);
  w += " || najkrotszy >50us: " + (min50 == 0xFFFFFFFF ? String("-") : String(min50));
  w += " | >100us: " + (min100 == 0xFFFFFFFF ? String("-") : String(min100));
  w += " | >300us: " + (min300 == 0xFFFFFFFF ? String("-") : String(min300));
  http.send(200, "text/plain", w);
}

// Surowy przebieg z linii odbiorczej: długości kolejnych odcinków L/H w µs,
// od pierwszego zbocza po co najmniej 20 ms spoczynku.
void httpSurowe() {
  zwolnijPinRx();
  pinMode(PIN_RX, INPUT);
  uint32_t t0 = millis();
  int lv = digitalRead(PIN_RX);
  uint32_t ostatnie = micros();
  while (millis() - t0 < 1200) {
    int p = digitalRead(PIN_RX);
    if (p != lv) { lv = p; ostatnie = micros(); }
    if (micros() - ostatnie > 20000) break;
  }
  t0 = millis();
  while (digitalRead(PIN_RX) == lv && millis() - t0 < 1200) {}
  static uint32_t zb[400];
  uint16_t n = 0;
  int poprz = digitalRead(PIN_RX);
  int pierwszy = poprz;
  uint32_t start = micros(), tp = start;
  while (micros() - start < 330000 && n < 400) {
    int p = digitalRead(PIN_RX);
    if (p != poprz) { uint32_t t = micros(); zb[n++] = t - tp; tp = t; poprz = p; }
  }
  uruchomOdbiornik(false);
  String w = "odcinkow: " + String(n) + "  ";
  for (uint16_t i = 0; i < n; i++) { w += String(zb[i]); w += (((i & 1) ? !pierwszy : pierwszy) ? "H " : "L "); }
  http.send(200, "text/plain", w);
}

// Polaryzacja sygnału: /mk?odwroc=0|1 przestawia odwracanie w układzie UART
// i zeruje liczniki. Przy magistrali Gree obowiązuje 1.
void httpMk() {
  if (http.hasArg("odwroc")) mkOdwroc = http.arg("odwroc").toInt() ? 1 : 0;
  mkBajty = 0; mkBledyRamki = 0; mkPrzepelnien = 0;
  stan.ramekOK = 0; stan.ramekZlaSuma = 0;
  bufLen = 0;
  uruchomOdbiornik(false);
  http.send(200, "text/plain", String("odwrocenie=") + mkOdwroc + ", liczniki wyzerowane");
}

// Diagnoza tego, co da się sprawdzić bez przewodu do pola EN: czy na linii
// cokolwiek się dzieje i czy wyjście odbiornika w ogóle nią steruje.
void httpDiag() {
  zwolnijPinRx();
  pinMode(PIN_RX, INPUT_PULLUP);
  delay(3);
  int zPod = digitalRead(PIN_RX);
  pinMode(PIN_RX, INPUT);
  delay(3);
  uint32_t zmian = 0, wysokich = 0, probek = 0;
  int poprz = digitalRead(PIN_RX);
  unsigned long doKiedy = millis() + 1000;
  while (millis() < doKiedy) {
    int teraz = digitalRead(PIN_RX);
    if (teraz != poprz) { zmian++; poprz = teraz; }
    if (teraz) wysokich++;
    probek++;
  }
  uruchomOdbiornik(false);
  String w;
  w += "1. linia w 1 s: zmian=" + String(zmian) + ", wysoko=" + String((100.0 * wysokich) / probek, 1) + "%" +
       (zmian > 50 ? "   (ok: magistrala nadaje)" : "   => LINIA STOI: brak sygnalu z jednostki albo przerwa A/B") + "\n";
  w += "2. podciagniecie w gore: " + String(zPod) +
       (zPod == 0 ? "   (ok: wyjscie odbiornika steruje linia)" : "   => nikt nie trzyma linii nisko; sprawdz zasilanie modulu i drut EN-GND") + "\n";
  w += "3. port szeregowy: bajtow=" + String(mkBajty) + ", bledow ramki=" + String(mkBledyRamki) +
       ", przepelnien=" + String(mkPrzepelnien) + ", odwracanie=" + String(mkOdwroc) + "\n";
  w += "4. ramki: poprawnych=" + String(stan.ramekOK) + ", z bledna suma=" + String(stan.ramekZlaSuma) + "\n";
  http.send(200, "text/plain", w);
}

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
  j += ",\"mk_bajty\":" + String(mkBajty);
  j += ",\"mk_bledy_stopu\":" + String(mkBledyRamki);
  j += ",\"mk_przepelnien\":" + String(mkPrzepelnien);
  j += ",\"mk_odwroc\":" + String(mkOdwroc);
  j += ",\"temp_procesora_c\":null";
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
  j += ",\"modul\":\"" + String(NAZWA_OTA) + "\"";
  j += ",\"plytka\":\"wemos-d1r1\"";
  j += ",\"wolna_pamiec\":" + String(ESP.getFreeHeap());
  j += ",\"min_wolna_pamiec\":" + String(minWolnejPamieci);
  j += ",\"uptime_s\":" + String(millis() / 1000);
  j += "}";
  http.send(200, "application/json", j);
}

void httpUstaw() {
  przejmijZamiar();   // gdyby komenda przyszła przed pierwszą ramką — nic nie robi
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
  h += String(NAZWA_OTA) + " (WeMos D1 R1)</h2><pre>";
  h += "temperatura pomieszczenia : " + String(stan.tempPokoj) + " C\n";
  h += "temperatura wymiennika    : " + String(stan.tempWymiennik) + " C\n";
  h += "wentylator                : " + String(nazwaBiegu(stan.bieg)) + "\n";
  h += "klapy                     : " + String(stan.klapy ? "otwarte" : "zamkniete") + "\n\n";
  h += "ramek poprawnych          : " + String(stan.ramekOK) + "\n";
  h += "ramek z bledna suma       : " + String(stan.ramekZlaSuma) + "\n";
  h += "cisza na magistrali       : " + String((millis() - ostatniBajtMs) / 1000) + " s\n\n";
  h += "nastawa                   : " + String(zad.temp) + " C, " + nazwaTrybu(zad.tryb) +
       ", bieg " + nazwaWent(zad.went) + (zad.wl ? ", wlaczony" : ", wylaczony") + "\n";
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
  emit("[CMD] nieznane. Dostepne: INFO, RESET, IR ON/OFF/SEND, IR TEMP n, IR TRYB x, IR WENT x\n");
}

// ── start ─────────────────────────────────────────────────────────────────
void setup() {
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);          // dioda zgaszona (świeci stanem niskim)

  Serial.begin(115200);                 // konsola USB — tylko do chwili startu odbiornika
  delay(80);
  emit("\n=== MODUL v2 (" + String(NAZWA_OTA) + ") — WeMos D1 R1, ESP8266 ===\n");

  EEPROM.begin(64);
  bool wczytane = czytajNastawy();
  emit(wczytane ? "[NASTAWY] wczytane z pamieci\n" : "[NASTAWY] pamiec pusta — wartosci domyslne\n");

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.setSleepMode(WIFI_NONE_SLEEP);   // stabilniejszy odbiór przy ciągłym nasłuchu
  WiFi.setAutoReconnect(true);
  WiFi.hostname(NAZWA_OTA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  // Czekamy na sieć jeszcze z konsolą na USB, żeby przy pierwszym wgraniu
  // było widać adres. Po 20 s idziemy dalej — moduł dołączy do sieci sam.
  unsigned long doKiedy = millis() + 20000;
  while (WiFi.status() != WL_CONNECTED && millis() < doKiedy) { delay(250); emit("."); }
  if (WiFi.status() == WL_CONNECTED) {
    wifiBylo = true;
    emit("\n[WiFi] POLACZONO, IP: " + WiFi.localIP().toString() + "\n");
  } else {
    emit("\n[WiFi] brak polaczenia, probuje dalej w tle\n");
  }

  telnet.begin();

  http.on("/stan",   httpStan);
  http.on("/ustaw",  httpUstaw);
  http.on("/linia",  httpLinia);
  http.on("/pin",    httpPin);
  http.on("/zrzut",  httpZrzut);
  http.on("/bity",   httpBity);
  http.on("/surowe", httpSurowe);
  http.on("/mk",     httpMk);
  http.on("/diag",   httpDiag);
  http.on("/",       httpStrona);
  http.begin();

  klima.begin();

  ArduinoOTA.setHostname(NAZWA_OTA);
  ArduinoOTA.setPort(PORT_OTA);
  ArduinoOTA.begin();

  startMs = millis();
  ostatniBajtMs = millis();
  uruchomOdbiornik(true);               // od tej chwili UART0 należy do magistrali
}

// ── pętla główna: nic jej nie blokuje ─────────────────────────────────────
// Dioda na module: szybkie migotanie = idą dane z magistrali, wolne = WiFi bez
// danych, bardzo szybkie = szuka sieci. Brak migania = procesor nie pracuje.
void migajStanem() {
  static unsigned long ledMs = 0;
  static bool ledStan = false;
  unsigned long okres;
  if (millis() - ostatniBajtMs < 600) okres = 60;
  else okres = (WiFi.status() == WL_CONNECTED) ? 1500 : 150;
  if (millis() - ledMs >= okres) {
    ledMs = millis();
    ledStan = !ledStan;
    digitalWrite(PIN_LED, ledStan ? LOW : HIGH);   // dioda świeci stanem niskim
  }
}

void loop() {
  migajStanem();
  ArduinoOTA.handle();
  http.handleClient();

  odbieraj();
  obsluzWeryfikacje();

  // strażnik pamięci: restart zamiast cichego zawieszenia.
  // Progi są niższe niż w ESP32 — ESP8266 ma ok. 30–40 kB wolnej sterty.
  if (millis() - ostatniaKontrolaPam > 5000) {
    ostatniaKontrolaPam = millis();
    uint32_t wolna = ESP.getFreeHeap();
    if (wolna < minWolnejPamieci) minWolnejPamieci = wolna;
    if (wolna < 6000) {
      emit("[STRAZNIK] pamiec " + String(wolna) + " B — restart\n");
      delay(300);
      ESP.restart();
    }
    if (wolna < 12000 && ring.length() > 600) ring = ring.substring(ring.length() - 600);
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
    klient.print("=== MODUL v2 (" + String(NAZWA_OTA) + ", WeMos D1 R1) ===\n--- HISTORIA ---\n");
    klient.print(ring);
    klient.print("\n--- NA ZYWO ---\n");
  }

  while (klient && klient.connected() && klient.available()) {
    char c = klient.read();
    if (c == '\n') { obsluzKomende(liniaCmd); liniaCmd = ""; }
    else if (c != '\r' && liniaCmd.length() < 200) liniaCmd += c;
  }
}
