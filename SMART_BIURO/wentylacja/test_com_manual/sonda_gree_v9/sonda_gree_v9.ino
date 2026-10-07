/*
 * SONDA COM-MANUAL v8 — Gree GKH / plyta GRZ4M-A3
 * ================================================
 * Napisana od nowa. Zasady, ktore v7 lamal:
 *  1. GLOWNA PETLA NIGDY SIE NIE BLOKUJE. Zaden tryb nie robi "return" przed
 *     obsluga komend — inaczej wlaczony tryb odcina zdalne sterowanie na stale.
 *  2. KAZDY TRYB MA TWARDY LIMIT CZASU (fala max 180 s) i konczy sie sam.
 *  3. NADAWANIE OKRESOWE DOMYSLNIE WYLACZONE — sonda po starcie tylko slucha,
 *     zeby nie zajmowac magistrali bez potrzeby.
 *  4. Jest komenda RESET (zdalny restart) — awaryjne wyjscie bez drabiny.
 *
 * Polaczenia (bramka GRZ47-G jako konwerter UART<->RS485):
 *   D6 = GPIO12 -> CN2 "TXD"      (nadawanie; opisy CN2 sa z perspektywy klimatyzatora)
 *   D5 = GPIO14 <- CN2 "RXD" przez dzielnik 3,3k/6,5k
 *   D7 = GPIO13 -> CN2 TXP        (klucz nadawania)
 *   GND -> CN2 GND oraz CN2 RXP   (odbiornik wlaczony na stale)
 *   5V  -> CN2 +5V                (ZASILAC Z micro-USB, nie z gniazda jack!)
 *
 * Komendy przez telnet (port 23), jedna na linie:
 *   TX <hex...>   wyslij dokladnie te bajty
 *   TXX <hex...>  wyslij + dolacz sume XOR
 *   SET <hex...> / SETX <hex...>   ustaw ramke okresowa (SETX = z auto-XOR)
 *   START / STOP  wlacz/wylacz nadawanie okresowe
 *   T <ms>        odstep nadawania okresowego (500..60000)
 *   PORX <ms>     nadawaj dopiero po N ms ciszy na magistrali (0 = asynchronicznie)
 *   POWT <n>      ile razy powtorzyc ramke (1..20)
 *   DEHOLD <ms>   ile trzymac klucz nadawania po ostatnim bajcie (0..200)
 *   INTTX 0|1     przerwania podczas nadawania (0 = precyzyjne bity)
 *   DEOFF 0|1     1 = nie podnos klucza (test: nic nie idzie na magistrale)
 *   FALA <s>      fala probiercza do pomiaru miernikiem (0 = stop, max 180)
 *   INFO          wypisz konfiguracje i statystyki
 *   RESET         restart sondy
 *
 * HTTP: /        podglad w przegladarce
 *       /stan    JSON dla Home Assistant
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <SoftwareSerial.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ir_Gree.h>
#include <IRac.h>

// ── konfiguracja stala ────────────────────────────────────────────────────
const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";

const uint8_t PIN_RX  = 14;   // D13/SCK/D5
const uint8_t PIN_TX  = 12;   // D12/MISO/D6
const uint8_t PIN_DIR = 13;   // D11/MOSI/D7

const unsigned long ODSTEP_BEACON_MS = 2000UL;
const unsigned long FALA_MAX_S       = 180UL;   // twardy limit trybu fali
const int OFFSET_TEMP = 100;                    // bajt - 100 = stopnie C

// ── obiekty ───────────────────────────────────────────────────────────────
SoftwareSerial gree;
WiFiServer telnet(23);
WiFiClient klient;
WiFiUDP udp;
ESP8266WebServer http(80);

// ── stan jednostki (z rozgloszenia FF->40) ────────────────────────────────
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


// ---- STEROWANIE PODCZERWIENIA ----
const uint8_t PIN_IR = 4;          // D14/SDA/D4 = GPIO4
IRGreeAC klima(PIN_IR);

struct Zadane {
  bool     wl    = false;
  uint8_t  temp  = 22;
  uint8_t  tryb  = kGreeCool;      // kGreeAuto/Cool/Dry/Fan/Heat
  uint8_t  went  = kGreeFanAuto;   // 0=auto 1=min 2=sred 3=max
  bool     swing = false;
  uint8_t  model = 1;              // 1=YAW1F 2=YBOFB 3=YX1FSF
  uint32_t wyslanych = 0;
} zad;

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


// Czysta nosna 38 kHz na pinie IR - do pomiaru amperomierzem
void nosna38kHz(uint16_t sekundy) {
  if (sekundy > 15) sekundy = 15;
  pinMode(PIN_IR, OUTPUT);
  emit("[IR] nosna 38 kHz przez " + String(sekundy) + " s - patrz na amperomierz\n");
  for (uint16_t s = 0; s < sekundy; s++) {
    unsigned long koniec = millis() + 1000;
    while (millis() < koniec) {
      digitalWrite(PIN_IR, HIGH);
      delayMicroseconds(13);
      digitalWrite(PIN_IR, LOW);
      delayMicroseconds(13);
    }
    yield();
  }
  digitalWrite(PIN_IR, LOW);
  emit("[IR] koniec nosnej\n");
}


// ---- PRZEMIAT PROTOKOLOW: wysyla 'wylacz' kolejnymi protokolami AC ----
IRac acUniw(PIN_IR);
const decode_type_t PROTOKOLY[] = {
  decode_type_t::GREE, decode_type_t::KELVINATOR, decode_type_t::COOLIX,
  decode_type_t::MIDEA, decode_type_t::TCL112AC, decode_type_t::HAIER_AC,
  decode_type_t::HAIER_AC_YRW02, decode_type_t::ELECTRA_AC, decode_type_t::GOODWEATHER,
  decode_type_t::AIRWELL, decode_type_t::TECO, decode_type_t::VESTEL_AC,
  decode_type_t::WHIRLPOOL_AC, decode_type_t::SAMSUNG_AC, decode_type_t::LG,
  decode_type_t::MITSUBISHI_AC, decode_type_t::DAIKIN, decode_type_t::PANASONIC_AC,
  decode_type_t::HITACHI_AC, decode_type_t::TROTEC, decode_type_t::ARGO,
  decode_type_t::CARRIER_AC, decode_type_t::DELONGHI_AC, decode_type_t::SANYO_AC
};
const uint8_t ILE_PROTOKOLOW = sizeof(PROTOKOLY) / sizeof(PROTOKOLY[0]);

void wyslijProtokolem(uint8_t idx, bool wlacz) {
  if (idx >= ILE_PROTOKOLOW) return;
  stdAc::state_t s;
  s.protocol = PROTOKOLY[idx];
  s.model    = 1;
  s.power    = wlacz;
  s.mode     = stdAc::opmode_t::kCool;
  s.degrees  = 24;
  s.celsius  = true;
  s.fanspeed = stdAc::fanspeed_t::kMedium;
  s.swingv   = stdAc::swingv_t::kOff;
  s.swingh   = stdAc::swingh_t::kOff;
  s.light = true; s.beep = true; s.econo = false; s.filter = false;
  s.turbo = false; s.quiet = false; s.clean = false; s.sleep = -1; s.clock = -1;
  if (acUniw.isProtocolSupported(s.protocol)) {
    acUniw.sendAc(s, &s);
    zad.wyslanych++;
    emit("[IR] protokol " + String(typeToString(s.protocol)) + " -> wyslany\n");
  } else {
    emit("[IR] protokol " + String(typeToString(s.protocol)) + " nieobslugiwany\n");
  }
}
void wyslijIRcicho() {
  switch (zad.model) {
    case 2:  klima.setModel(gree_ac_remote_model_t::YBOFB); break;
    case 3:  klima.setModel(gree_ac_remote_model_t::YX1FSF); break;
    default: klima.setModel(gree_ac_remote_model_t::YAW1F); break;
  }
  klima.setPower(zad.wl);
  klima.setTemp(zad.temp);
  klima.setMode(zad.tryb);
  klima.setFan(zad.went);
  klima.send();
  zad.wyslanych++;
}

// Ciagle wysylanie ramki Gree przez biblioteke - do pomiaru amperomierzem
void serialIR(uint16_t sekundy) {
  if (sekundy > 20) sekundy = 20;
  emit("[IR] seria ramek przez " + String(sekundy) + " s - patrz na amperomierz\n");
  unsigned long koniec = millis() + (unsigned long)sekundy * 1000UL;
  uint16_t ile = 0;
  while (millis() < koniec) {
    wyslijIRcicho();
    ile++;
    yield();
  }
  emit("[IR] koniec serii, ramek: " + String(ile) + "\n");
}
void wyslijIR() {
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
  klima.send();
  zad.wyslanych++;
  emit("[IR] wyslano: wl=" + String(zad.wl) + " temp=" + String(zad.temp) +
       " tryb=" + String(nazwaTrybu(zad.tryb)) + " went=" + String(nazwaWent(zad.went)) +
       " swing=" + String(zad.swing) + " model=" + String(zad.model) + "\n");
}

// ── parametry nadawania ───────────────────────────────────────────────────
bool          intTxWl     = false;
unsigned int  deHoldMs    = 8;
unsigned int  poRxMs      = 0;
uint8_t       powtorzen   = 1;
bool          nadajnikWyl = false;

uint8_t  ramkaOkresowa[48] = {
  0x7E,0x7E,0x00,0xFF,0x11,0x0E,0x00,0x00,0x02,0x01,
  0x89,0x8A,0xBE,0x47,0x00,0x80,0x00,0x00,0x00,0x99
};
uint8_t  dlOkresowa   = 20;
bool     autoXorOkres = false;
bool     okresoweWl   = false;          // DOMYSLNIE WYLACZONE
unsigned long odstepMs = 3000UL;

// ── stan trybu fali (maszyna stanow, nie blokuje petli) ───────────────────
unsigned long falaDo        = 0;
unsigned long falaOstatniaMs = 0;
bool          falaPoziom    = true;

// ── bufory i liczniki ─────────────────────────────────────────────────────
unsigned long startMs = 0, ostatniaSonda = 0, ostatniBajtMs = 0, ostatniBeacon = 0;
uint8_t  buf[64];
uint8_t  bufLen = 0;
String   ring;
const unsigned int RING_MAX = 1500;
bool     wifiBylo = false;
String   liniaCmd;
uint32_t licznikTx = 0;
unsigned long irPinDo = 0;   // do kiedy pin IR trzymany na stale
const uint8_t PINY_WOLNE[] = {4, 5, 16, 2, 0, 15};
const uint8_t ILE_WOLNYCH = 6;
int skanPin = -1;              // -1 = brak skanu, inaczej indeks
unsigned long skanDo = 0;
unsigned long ostatniaKontrolaPam = 0;
uint32_t minWolnejPamieci = 0xFFFFFFFF;
uint32_t minBloku = 0xFFFFFFFF;

// ── narzedzia ─────────────────────────────────────────────────────────────
void emit(const String& s) {
  Serial.print(s);
  ring += s;
  if (ring.length() > RING_MAX) ring.remove(0, ring.length() - RING_MAX);
  if (klient && klient.connected()) klient.print(s);
}

String hex2(uint8_t b) {
  String s = String(b, HEX);
  if (s.length() < 2) s = "0" + s;
  s.toUpperCase();
  return s + " ";
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

// ── analiza odebranych ramek ──────────────────────────────────────────────
void analizujBufor() {
  while (bufLen >= 6) {
    if (buf[0] != 0x7E || buf[1] != 0x7E) { memmove(buf, buf + 1, --bufLen); continue; }
    uint8_t dlBody = buf[5];
    uint8_t total  = 6 + dlBody;
    if (total > sizeof(buf) || dlBody == 0) { memmove(buf, buf + 2, bufLen -= 2); continue; }
    if (bufLen < total) return;

    uint8_t x = 0;
    for (uint8_t i = 0; i < total - 1; i++) x ^= buf[i];
    bool ok = (x == buf[total - 1]);

    String s = "\n>>> RAMKA (";
    s += ok ? "SUMA OK" : "suma bledna";
    s += "): ";
    for (uint8_t i = 0; i < total; i++) s += hex2(buf[i]);
    emit(s + "\n");

    if (ok) {
      stan.ramekOK++;
      if (total == 29 && buf[2] == 0xFF && buf[3] == 0x40 && buf[5] == 0x17) {
        stan.tempPokoj     = (int)buf[9]  - OFFSET_TEMP;
        stan.tempWymiennik = (int)buf[10] - OFFSET_TEMP;
        stan.bieg          = buf[12];
        stan.klapy         = (buf[14] & 0x80) != 0;
        stan.ostatniaMs    = millis();
        stan.jest          = true;
      }
    } else {
      stan.ramekZlaSuma++;
    }
    memmove(buf, buf + total, bufLen -= total);
  }
}

void odbieraj() {
  while (gree.available()) {
    uint8_t b = gree.read();
    if (millis() - ostatniBajtMs > 200) emit("\n[RX t=" + String(millis()) + "] ");
    ostatniBajtMs = millis();
    emit(hex2(b));
    if (bufLen < sizeof(buf)) buf[bufLen++] = b;
    analizujBufor();
  }
}

// ── nadawanie ─────────────────────────────────────────────────────────────
void wyslijRaz(uint8_t* dane, uint8_t n) {
  if (!nadajnikWyl) digitalWrite(PIN_DIR, HIGH);
  delayMicroseconds(200);
  gree.write(dane, n);
  gree.flush();
  delay(deHoldMs);
  digitalWrite(PIN_DIR, LOW);
  licznikTx++;
}

void wyslij(const uint8_t* dane, uint8_t n, bool autoXor, const char* etyk) {
  uint8_t r[50];
  memcpy(r, dane, n);
  uint8_t total = n;
  if (autoXor && total < 49) {
    uint8_t x = 0;
    for (uint8_t i = 0; i < total; i++) x ^= r[i];
    r[total++] = x;
  }
  String s = "\n[" + String(etyk) + " " + String(millis() / 1000.0, 1) + "s] ";
  for (uint8_t i = 0; i < total; i++) s += hex2(r[i]);
  emit(s + "\n");

  for (uint8_t p = 0; p < powtorzen; p++) {
    if (poRxMs > 0) {                       // czekaj na cisze, ale nie w nieskonczonosc
      unsigned long limit = millis() + 3000;
      while (millis() < limit) {
        odbieraj();
        if (millis() - ostatniBajtMs >= poRxMs) break;
        yield();
      }
    }
    wyslijRaz(r, total);
    if (p + 1 < powtorzen) delay(40);
  }
}

// ── komendy ───────────────────────────────────────────────────────────────
int parsujHex(const String& l, int od, uint8_t* wy, int maxN) {
  int n = 0, i = od;
  while (i < (int)l.length() && n < maxN) {
    while (i < (int)l.length() && l[i] == ' ') i++;
    if (i >= (int)l.length()) break;
    int j = i;
    while (j < (int)l.length() && l[j] != ' ') j++;
    String tok = l.substring(i, j);
    tok.trim();
    if (tok.length()) {
      char* koniec;
      long v = strtol(tok.c_str(), &koniec, 16);
      if (*koniec != 0 || v < 0 || v > 255) return -1;
      wy[n++] = (uint8_t)v;
    }
    i = j;
  }
  return n;
}

void obsluzKomende(String l) {
  l.trim();
  if (!l.length()) return;
  String D = l; D.toUpperCase();
  uint8_t tmp[48];

  if (D.startsWith("SERIA ")) { serialIR(D.substring(6).toInt()); return; }
  if (D.startsWith("NOSNA ")) { nosna38kHz(D.substring(6).toInt()); return; }
  if (D.startsWith("PINY ")) {
    long sek = D.substring(5).toInt(); if (sek <= 0) sek = 60; if (sek > 300) sek = 300;
    for (uint8_t k = 0; k < ILE_WOLNYCH; k++) { pinMode(PINY_WOLNE[k], OUTPUT); digitalWrite(PINY_WOLNE[k], HIGH); }
    irPinDo = millis() + (unsigned long)sek * 1000UL;
    skanPin = -1;
    emit("[IR] WSZYSTKIE wolne piny WYSOKO na " + String(sek) + " s\n");
    return;
  }
  if (D == "SKAN") {
    for (uint8_t k = 0; k < ILE_WOLNYCH; k++) { pinMode(PINY_WOLNE[k], OUTPUT); digitalWrite(PINY_WOLNE[k], LOW); }
    skanPin = 0; skanDo = millis() + 8000UL;
    digitalWrite(PINY_WOLNE[0], HIGH);
    emit("[IR] SKAN: GPIO" + String(PINY_WOLNE[0]) + " wysoko (8 s)\n");
    return;
  }
  if (D.startsWith("IRPIN ")) {
    long sek = D.substring(6).toInt();
    if (sek <= 0) { irPinDo = 0; pinMode(PIN_IR, OUTPUT); digitalWrite(PIN_IR, LOW);
      emit("[IR] pin zgaszony\n"); return; }
    if (sek > 300) sek = 300;
    irPinDo = millis() + (unsigned long)sek * 1000UL;
    pinMode(PIN_IR, OUTPUT);
    digitalWrite(PIN_IR, HIGH);
    emit("[IR] pin GPIO4 trzymany WYSOKO przez " + String(sek) + " s - mierz miernikiem\n");
    return;
  }
  if (D.startsWith("IR ")) {
    String a = D.substring(3); a.trim();
    if (a == "ON")       { zad.wl = true;  wyslijIR(); }
    else if (a == "OFF") { zad.wl = false; wyslijIR(); }
    else if (a == "SEND"){ wyslijIR(); }
    else if (a.startsWith("TEMP ")) { long v = a.substring(5).toInt();
        if (v >= 16 && v <= 30) { zad.temp = v; wyslijIR(); } else emit("[IR] temp 16..30\n"); }
    else if (a.startsWith("TRYB ")) { String m = a.substring(5); m.trim();
        if (m == "AUTO") zad.tryb = kGreeAuto; else if (m == "COOL") zad.tryb = kGreeCool;
        else if (m == "DRY") zad.tryb = kGreeDry; else if (m == "FAN") zad.tryb = kGreeFan;
        else if (m == "HEAT") zad.tryb = kGreeHeat; else { emit("[IR] tryb: AUTO/COOL/DRY/FAN/HEAT\n"); return; }
        wyslijIR(); }
    else if (a.startsWith("WENT ")) { String f = a.substring(5); f.trim();
        if (f == "AUTO") zad.went = kGreeFanAuto; else if (f == "1") zad.went = kGreeFanMin;
        else if (f == "2") zad.went = kGreeFanMed; else if (f == "3") zad.went = kGreeFanMax;
        else { emit("[IR] went: AUTO/1/2/3\n"); return; }
        wyslijIR(); }
    else if (a.startsWith("SWING ")) { zad.swing = a.substring(6).toInt() != 0; wyslijIR(); }
    else if (a.startsWith("MODEL ")) { long v = a.substring(6).toInt();
        if (v >= 1 && v <= 3) { zad.model = v; emit("[IR] model=" + String(v) + "\n"); } }
    else emit("[IR] ON/OFF/SEND/TEMP n/TRYB x/WENT x/SWING 0|1/MODEL 1-3\n");
    return;
  }
  if (D == "STOP")  { okresoweWl = false; falaDo = 0; digitalWrite(PIN_DIR, LOW);
                      emit("[CMD] STOP: nadawanie okresowe i fala wylaczone\n"); return; }
  if (D == "START") { okresoweWl = true;  emit("[CMD] nadawanie okresowe: START\n"); return; }
  if (D == "RESET") { emit("[CMD] restart sondy...\n"); delay(200); ESP.restart(); return; }
  if (D == "INFO") {
    String s = "[CMD] okres=" + String(odstepMs) + "ms wl=" + String(okresoweWl)
             + " autoXor=" + String(autoXorOkres) + " intTx=" + String(intTxWl)
             + " deHold=" + String(deHoldMs) + " poRx=" + String(poRxMs)
             + " powt=" + String(powtorzen) + " nadajnikWyl=" + String(nadajnikWyl)
             + " fala=" + String(falaDo > millis() ? (falaDo - millis()) / 1000 : 0) + "s"
             + " | RX ok=" + String(stan.ramekOK) + " zle=" + String(stan.ramekZlaSuma)
             + " TX=" + String(licznikTx)
             + " | od ostatniego bajtu: " + String((millis() - ostatniBajtMs) / 1000) + "s"
             + " | ramka: ";
    for (uint8_t i = 0; i < dlOkresowa; i++) s += hex2(ramkaOkresowa[i]);
    emit(s + "\n");
    return;
  }
  if (D.startsWith("FALA ")) {
    long s = D.substring(5).toInt();
    if (s <= 0) { falaDo = 0; digitalWrite(PIN_DIR, LOW); emit("[CMD] fala: STOP\n"); return; }
    if ((unsigned long)s > FALA_MAX_S) s = FALA_MAX_S;
    falaDo = millis() + (unsigned long)s * 1000UL;
    emit("[CMD] fala probiercza " + String(s) + " s (mierz A-B); STOP przerywa\n");
    return;
  }
  if (D.startsWith("T ")) {
    long v = D.substring(2).toInt();
    if (v >= 500 && v <= 60000) { odstepMs = v; emit("[CMD] okres=" + String(v) + "ms\n"); }
    else emit("[CMD] BLAD: T 500..60000\n");
    return;
  }
  if (D.startsWith("PORX "))   { long v = D.substring(5).toInt();  if (v >= 0 && v <= 2000) { poRxMs = v;    emit("[CMD] poRx=" + String(v) + "ms\n"); } return; }
  if (D.startsWith("POWT "))   { long v = D.substring(5).toInt();  if (v >= 1 && v <= 20)   { powtorzen = v; emit("[CMD] powt=" + String(v) + "\n"); } return; }
  if (D.startsWith("DEHOLD ")) { long v = D.substring(7).toInt();  if (v >= 0 && v <= 200)  { deHoldMs = v;  emit("[CMD] deHold=" + String(v) + "ms\n"); } return; }
  if (D.startsWith("INTTX "))  { intTxWl = D.substring(6).toInt() != 0; gree.enableIntTx(intTxWl); emit("[CMD] intTx=" + String(intTxWl) + "\n"); return; }
  if (D.startsWith("DEOFF "))  { nadajnikWyl = D.substring(6).toInt() != 0; emit("[CMD] nadajnikWyl=" + String(nadajnikWyl) + "\n"); return; }

  if (D.startsWith("SETX ") || D.startsWith("SET ")) {
    bool ax = D.startsWith("SETX ");
    int n = parsujHex(D, ax ? 5 : 4, tmp, sizeof(tmp));
    if (n <= 0) { emit("[CMD] BLAD: zle bajty\n"); return; }
    memcpy(ramkaOkresowa, tmp, n); dlOkresowa = n; autoXorOkres = ax;
    emit("[CMD] nowa ramka okresowa (" + String(n) + " B, autoXor=" + String(ax) + ")\n");
    return;
  }
  if (D.startsWith("TXX ") || D.startsWith("TX ")) {
    bool ax = D.startsWith("TXX ");
    int n = parsujHex(D, ax ? 4 : 3, tmp, sizeof(tmp));
    if (n <= 0) { emit("[CMD] BLAD: zle bajty\n"); return; }
    wyslij(tmp, n, ax, "TX-CMD");
    return;
  }
  emit("[CMD] nieznana komenda: " + l + "\n");
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
  j += ",\"wyslanych\":" + String(licznikTx);
  j += ",\"cisza_na_magistrali_s\":" + String((millis() - ostatniBajtMs) / 1000);
  j += ",\"fala_s\":" + String(falaDo > millis() ? (falaDo - millis()) / 1000 : 0);
  j += ",\"zad_wl\":" + String(zad.wl ? "true" : "false");
  j += ",\"zad_temp\":" + String(zad.temp);
  j += ",\"zad_tryb\":\"" + String(nazwaTrybu(zad.tryb)) + "\"";
  j += ",\"zad_went\":\"" + String(nazwaWent(zad.went)) + "\"";
  j += ",\"zad_swing\":" + String(zad.swing ? "true" : "false");
  j += ",\"ir_model\":" + String(zad.model);
  j += ",\"ir_wyslanych\":" + String(zad.wyslanych);
  j += ",\"wolna_pamiec\":" + String(ESP.getFreeHeap());
  j += ",\"min_wolna_pamiec\":" + String(minWolnejPamieci);
  j += ",\"blok_pamieci\":" + String(ESP.getMaxFreeBlockSize());
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
  if (zmiana || http.hasArg("send")) wyslijIR();
  httpStan();
}

void httpStrona() {
  String h = "<meta charset=\"utf-8\"><title>Sonda Gree</title><h2>Sonda Gree v8</h2><pre>";
  h += "temperatura pomieszczenia : " + String(stan.tempPokoj) + " C\n";
  h += "temperatura wymiennika    : " + String(stan.tempWymiennik) + " C\n";
  h += "wentylator                : " + String(nazwaBiegu(stan.bieg)) + "\n";
  h += "klapy                     : " + String(stan.klapy ? "otwarte" : "zamkniete") + "\n\n";
  h += "ramek poprawnych          : " + String(stan.ramekOK) + "\n";
  h += "ramek z bledna suma       : " + String(stan.ramekZlaSuma) + "\n";
  h += "wyslanych przez sonde     : " + String(licznikTx) + "\n";
  h += "cisza na magistrali       : " + String((millis() - ostatniBajtMs) / 1000) + " s\n";
  h += "uptime                    : " + String(millis() / 1000) + " s\n";
  h += "</pre><p><a href=\"/stan\">/stan</a> — dane dla Home Assistant</p>";
  http.send(200, "text/html", h);
}

// ── start ─────────────────────────────────────────────────────────────────
void setup() {
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);
  Serial.begin(115200);
  gree.begin(1200, SWSERIAL_8N1, PIN_RX, PIN_TX);
  gree.enableIntTx(intTxWl);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  telnet.begin();

  http.on("/stan", httpStan);
  http.on("/prot", []() {
    uint8_t idx = http.hasArg("i") ? http.arg("i").toInt() : 0;
    bool wl = http.hasArg("wl") ? (http.arg("wl") == "1") : false;
    String nazwa = (idx < ILE_PROTOKOLOW) ? String(typeToString(PROTOKOLY[idx])) : String("?");
    http.send(200, "text/plain", String(idx) + ":" + nazwa + ":" + String(ILE_PROTOKOLOW));
    wyslijProtokolem(idx, wl);
  });
  http.on("/seria", []() {
    uint16_t s = http.hasArg("s") ? http.arg("s").toInt() : 10;
    httpStan();
    serialIR(s);
  });
  http.on("/nosna", []() {
    uint16_t s = http.hasArg("s") ? http.arg("s").toInt() : 8;
    httpStan();
    nosna38kHz(s);
  });
  http.on("/piny", []() {
    long sek = http.hasArg("s") ? http.arg("s").toInt() : 120;
    if (sek > 300) sek = 300;
    for (uint8_t k = 0; k < ILE_WOLNYCH; k++) { pinMode(PINY_WOLNE[k], OUTPUT); digitalWrite(PINY_WOLNE[k], HIGH); }
    irPinDo = millis() + (unsigned long)sek * 1000UL; skanPin = -1;
    httpStan();
  });
  http.on("/skan", []() {
    for (uint8_t k = 0; k < ILE_WOLNYCH; k++) { pinMode(PINY_WOLNE[k], OUTPUT); digitalWrite(PINY_WOLNE[k], LOW); }
    skanPin = 0; skanDo = millis() + 8000UL; digitalWrite(PINY_WOLNE[0], HIGH);
    httpStan();
  });
  http.on("/irpin", []() {
    long sek = http.hasArg("s") ? http.arg("s").toInt() : 60;
    if (sek <= 0) { irPinDo = 0; digitalWrite(PIN_IR, LOW); }
    else { if (sek > 300) sek = 300; irPinDo = millis() + (unsigned long)sek * 1000UL;
           pinMode(PIN_IR, OUTPUT); digitalWrite(PIN_IR, HIGH); }
    httpStan();
  });
  http.on("/ustaw", httpUstaw);
  http.on("/", httpStrona);
  http.begin();

  klima.begin();
  ArduinoOTA.setHostname("sonda-gree");
  ArduinoOTA.begin();

  startMs = millis();
  ostatniBajtMs = millis();
  emit("\n=== SONDA v9 (odczyt magistrali + sterowanie IR) — nasluch magistrali, nadawanie na zadanie ===\n");
}

// ── petla glowna: nic jej nie blokuje ─────────────────────────────────────
void loop() {
  ArduinoOTA.handle();
  http.handleClient();

  if (skanPin >= 0 && millis() > skanDo) {
    digitalWrite(PINY_WOLNE[skanPin], LOW);
    skanPin++;
    if (skanPin >= (int)ILE_WOLNYCH) { skanPin = -1;
      emit("[IR] SKAN zakonczony\n"); }
    else { digitalWrite(PINY_WOLNE[skanPin], HIGH); skanDo = millis() + 8000UL;
      emit("[IR] SKAN: GPIO" + String(PINY_WOLNE[skanPin]) + " wysoko (8 s)\n"); }
  }

  if (irPinDo > 0 && millis() > irPinDo) {   // koniec trybu testowego pinu IR
    irPinDo = 0;
    digitalWrite(PIN_IR, LOW);
    emit("[IR] koniec testu pinu\n");
  }

  // STRAZNIK PAMIECI: restart zamiast cichego zawieszenia
  if (millis() - ostatniaKontrolaPam > 5000) {
    ostatniaKontrolaPam = millis();
    uint32_t wolna = ESP.getFreeHeap();
    uint32_t blok  = ESP.getMaxFreeBlockSize();   // najwiekszy SPOJNY blok - to on decyduje
    if (wolna < minWolnejPamieci) minWolnejPamieci = wolna;
    if (blok < minBloku) minBloku = blok;
    if (wolna < 8000 || blok < 6000) {
      emit("[STRAZNIK] pamiec " + String(wolna) + " B, blok " + String(blok) + " B - restart\n");
      delay(300);
      ESP.restart();
    }
    if (wolna < 14000 && ring.length() > 800) ring = ring.substring(ring.length() - 800);
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
    udp.print("SONDA-GREE " + ip.toString());
    udp.endPacket();
  }

  if (telnet.hasClient()) {
    if (klient) klient.stop();
    klient = telnet.accept();
    liniaCmd = "";
    klient.print("=== SONDA v9 (odczyt magistrali + sterowanie IR) ===\n--- HISTORIA ---\n");
    klient.print(ring);
    klient.print("\n--- NA ZYWO ---\n");
  }

  // KOMENDY — zawsze obslugiwane, niezaleznie od trybu
  while (klient && klient.connected() && klient.available()) {
    char c = klient.read();
    if (c == '\n') { obsluzKomende(liniaCmd); liniaCmd = ""; }
    else if (c != '\r' && liniaCmd.length() < 200) liniaCmd += c;
  }

  // ODBIOR — zawsze, poza chwilami wlasnego nadawania
  odbieraj();

  // FALA — maszyna stanow, sama sie konczy, nie blokuje petli
  if (falaDo > millis()) {
    if (!nadajnikWyl) digitalWrite(PIN_DIR, HIGH);
    if (millis() - falaOstatniaMs > 1000) {
      falaOstatniaMs = millis();
      falaPoziom = !falaPoziom;
      digitalWrite(PIN_TX, falaPoziom ? HIGH : LOW);
    }
  } else if (falaDo != 0) {          // fala wlasnie sie skonczyla — posprzataj
    falaDo = 0;
    digitalWrite(PIN_DIR, LOW);
    digitalWrite(PIN_TX, HIGH);      // stan spoczynkowy linii
    emit("[CMD] fala zakonczona (limit czasu)\n");
  }

  // NADAWANIE OKRESOWE — tylko gdy wlaczone i gdy nie trwa fala
  if (okresoweWl && falaDo == 0 && millis() - startMs > 8000UL &&
      millis() - ostatniaSonda > odstepMs) {
    ostatniaSonda = millis();
    wyslij(ramkaOkresowa, dlOkresowa, autoXorOkres, "TX");
  }

  yield();
}
