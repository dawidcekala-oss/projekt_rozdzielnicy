/*
 * MODUŁ v2 — firmware ESP32
 *
 * Odczyt magistrali RS-485 klimatyzatora Gree GKH + sterowanie podczerwienią,
 * z weryfikacją każdej komendy przez magistralę.
 *
 * Wobec sondy v10 (ESP8266):
 *   - sprzętowy UART2 zamiast programowego  -> koniec ramek z błędną sumą,
 *   - nastawy w pamięci NVS zamiast EEPROM,
 *   - bez odbiornika podczerwieni: wykonanie komendy potwierdza magistrala,
 *     która co 800 ms podaje rzeczywisty stan jednostki. GPIO19 wolny.
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
#include <ir_Gree.h>
#include "soc/gpio_reg.h"
#include "esp_task_wdt.h"

// ── konfiguracja ──────────────────────────────────────────────────────────
const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";
// Numer egzemplarza: domyslnie 1; dla kolejnych modulow kompilowac z
//   --build-property "compiler.cpp.extra_flags=-DMODUL_NR=2"
// Nazwa OTA i mDNS to wtedy modul-gree-2, zrodlo pozostaje wspolne.
#ifndef MODUL_NR
#define MODUL_NR 1
#endif
#define MODUL_STR_(x) #x
#define MODUL_STR(x) MODUL_STR_(x)
const char* NAZWA_OTA = "modul-gree-" MODUL_STR(MODUL_NR);

// Numery GPIO. Opisy na płytce ESP32 DevKit 30-pin są inne — patrz kolumna "płytka".
//   GPIO16 -> RX2      GPIO17 -> TX2      GPIO4 -> D4
//   GPIO23 -> D23      GPIO19 -> D19      zasilanie 5 V -> pin VIN (nie "5V"!)
const uint8_t PIN_RX    = 17;   // TX2 na plytce <- pole TXD modulu = WYJSCIE odbiornika (opis z perspektywy modulu)   // RX2  <- RXD modułu RS485 V2.05
const uint8_t PIN_TX    = 16;   // RX2 na plytce -> pole RXD modulu = wejscie nadajnika   // TX2  -> TXD modułu RS485 V2.05
const uint8_t PIN_DIR   = 4;    // D4   -> DE/RE (NISKO = odbior)
const uint8_t PIN_IR_TX = 23;   // D23  -> baza tranzystora przez 470 Ω
const uint8_t PIN_LED_STAN = 2; // D2   -> dioda na plytce DevKita: sygnalizacja stanu

const unsigned long ODSTEP_BEACON_MS = 2000UL;
const int  OFFSET_TEMP   = 100;         // bajt magistrali − 100 = °C
const uint16_t PORT_HTTP = 80;

// ── obiekty ───────────────────────────────────────────────────────────────
HardwareSerial magistrala(2);
WebServer   http(PORT_HTTP);
WiFiServer  telnet(23);

struct Wariant { uint8_t rx, tx; bool en; bool inv; const char* opis; };
const Wariant WARIANTY[8] = {
  {16, 17, false, false, "wprost, kierunek nisko"},
  {17, 16, false, false, "RXD/TXD zamienione, kierunek nisko"},
  {16, 17, true,  false, "wprost, kierunek wysoko"},
  {17, 16, true,  false, "RXD/TXD zamienione, kierunek wysoko"},
  {16, 17, false, true,  "wprost, kierunek nisko, sygnal ODWROCONY (A/B zamienione)"},
  {17, 16, false, true,  "RXD/TXD zamienione, kierunek nisko, sygnal ODWROCONY"},
  {16, 17, true,  true,  "wprost, kierunek wysoko, sygnal ODWROCONY"},
  {17, 16, true,  true,  "RXD/TXD zamienione, kierunek wysoko, sygnal ODWROCONY"},
};
uint16_t skanBajtow[8] = {0, 0, 0, 0, 0, 0, 0, 0};
uint16_t skanZnacznikow[8] = {0, 0, 0, 0, 0, 0, 0, 0};
int8_t   wybranyWariant = -1;

WiFiClient  klient;
WiFiUDP     udp;
Preferences nvs;

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

bool nastawyZNvs    = false;   // true = zamiar wczytany z pamieci NVS
bool zamiarPrzejety = false;   // true = zamiar przejety z magistrali (pusta pamiec)
void przejmijZamiar();

// ── weryfikacja komendy przez magistralę ──────────────────────────────────
const unsigned long OKNO_WERYF_MS = 14000UL;
const uint8_t MAX_PONOWIEN = 2;
const uint8_t POWTORZEN_IR = 3;

unsigned long weryfDo           = 0;
uint8_t       ponowien          = 0;
int8_t        potwierdzone      = -1;   // -1 nieznane, 0 nie, 1 tak
unsigned long ostatniaKomendaMs = 0;

// ── nauka i echo podczerwieni ─────────────────────────────────────────────

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
  nastawyZNvs = jest;
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
    przejmijZamiar();

    memmove(buf, r + 29, bufLen - i - 29);
    bufLen -= (i + 29);
    return;
  }
  if (bufLen > 48) { memmove(buf, buf + bufLen - 32, 32); bufLen = 32; }
}

// ── miekki odbiornik magistrali ─────────────────────────────────
// Sprzetowy port szeregowy traktuje kazda szpilke jak bit startu. Ten
// odbiornik probkuje linie 16 razy na bit (co 52 us przy 1200 bd), a o
// wartosci bitu decyduje glosowanie 9 probek wokol jego srodka. Szpilka
// trwajaca 50 us przegrywa z bitem trwajacym 833 us.
// Po pustej pamieci domyslny zamiar to "wylaczony" - wtedy kazda czesciowa komenda
// (sam bieg, sama temperatura) gasilaby jednostke. Dlatego zamiar przejmujemy
// z pierwszej poprawnej ramki magistrali: wlaczony <=> wentylator != 0, bieg z kodu.
void przejmijZamiar() {
  if (zamiarPrzejety || nastawyZNvs || !stan.jest) return;
  zad.wl = (stan.bieg != 0);
  if      (stan.bieg == 0x04) zad.went = kGreeFanMin;
  else if (stan.bieg == 0x02) zad.went = kGreeFanMed;
  else if (stan.bieg == 0x01) zad.went = kGreeFanMax;
  zamiarPrzejety = true;
  emit(String("[NASTAWY] zamiar przejety z magistrali: ") + (zad.wl ? "wlaczony" : "wylaczony") +
       ", bieg " + nazwaWent(zad.went) + "\n");
}

hw_timer_t* probkowanie = nullptr;
volatile uint8_t  mkBuf[256];
volatile uint8_t  mkGlowa = 0, mkOgon = 0;
volatile uint32_t mkStarty = 0, mkBajty = 0, mkBledyStopu = 0;
volatile uint8_t  mkOkno = 0xFF;   // ostatnie 8 probek, bit0 = najnowsza
volatile uint8_t  mkStan = 0;      // 0 spoczynek, 1 w bajcie, 2 wstrzymanie po bledzie
volatile uint16_t mkPoz = 0;
volatile uint8_t  mkBit = 0, mkGlosy = 0, mkBajt = 0;
volatile uint8_t  mkOdwroc = 1;    // magistrala Gree: wyjscie odbiornika w spoczynku NISKO -> odwracamy

uint8_t IRAM_ATTR liczJedynki(uint8_t v) {
  v = v - ((v >> 1) & 0x55);
  v = (v & 0x33) + ((v >> 2) & 0x33);
  return (v + (v >> 4)) & 0x0F;
}

void IRAM_ATTR isrProbka() {
  uint8_t p = ((REG_READ(GPIO_IN_REG) >> PIN_RX) & 1) ^ mkOdwroc;
  mkOkno = (mkOkno << 1) | p;
  if (mkStan == 0) {
    if (liczJedynki(mkOkno) <= 2) {          // co najmniej 6 z 8 nisko: bit startu
      mkStan = 1; mkPoz = 7; mkBit = 0; mkGlosy = 0; mkBajt = 0;
      mkStarty++;
    }
    return;
  }
  if (mkStan == 2) {
    if (liczJedynki(mkOkno) >= 6) mkStan = 0; // linia wrocila do spoczynku
    return;
  }
  mkPoz++;
  uint16_t srodek = 16 * (mkBit + 1) + 8;
  if (mkPoz >= srodek - 4 && mkPoz <= srodek + 4) {
    mkGlosy += p;
    if (mkPoz == srodek + 4) {
      uint8_t wartosc = (mkGlosy >= 5) ? 1 : 0;
      mkGlosy = 0;
      if (mkBit < 8) {
        mkBajt |= (wartosc << mkBit);
        mkBit++;
      } else {                                  // bit stopu
        if (wartosc) {
          uint8_t nast = mkGlowa + 1;
          if (nast != mkOgon) { mkBuf[mkGlowa] = mkBajt; mkGlowa = nast; }
          mkBajty++;
          mkStan = 0;
        } else {
          mkBledyStopu++;
          mkStan = 2;
        }
      }
    }
  }
}

bool    mkDostepny() { return mkGlowa != mkOgon; }
uint8_t mkCzytaj()   { uint8_t b = mkBuf[mkOgon]; mkOgon = mkOgon + 1; return b; }

void uruchomMiekkiOdbiornik() {
  magistrala.end();
  pinMode(PIN_RX, INPUT);
  probkowanie = timerBegin(1000000);          // 1 MHz
  timerAttachInterrupt(probkowanie, &isrProbka);
  timerAlarm(probkowanie, 52, true, 0);       // co 52 us = 16 probek na bit
  emit("[MK] miekki odbiornik uruchomiony: 16 probek/bit, glosowanie 9 probek\n");
}

void odbieraj() {
  while (mkDostepny()) {
    uint8_t b = mkCzytaj();
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
// Surowy stan linii, ktora modul RS485 podaje procesorowi. Rozstrzyga, czy do
// modulu w ogole dociera sygnal, bez wchodzenia na drabine z oscyloskopem.
// Po kazdej diagnostyce piny wracaja do wejsc. Nigdy magistrala.begin():
// port sprzetowy zrobilby z pinu nadawczego wyjscie w stanie wysokim.
static void przywrocPiny() {
  magistrala.end();
  pinMode(PIN_RX, INPUT);
  pinMode(PIN_TX, INPUT);
  pinMode(PIN_DIR, OUTPUT); digitalWrite(PIN_DIR, LOW);
}

void httpLinia() {
  bool pod = http.hasArg("pullup");
  pinMode(PIN_RX, pod ? INPUT_PULLUP : INPUT);
  uint32_t zmian = 0, wysokich = 0, probek = 0;
  int poprz = digitalRead(PIN_RX);
  unsigned long doKiedy = millis() + 3000;
  while (millis() < doKiedy) {
    int teraz = digitalRead(PIN_RX);
    if (teraz != poprz) { zmian++; poprz = teraz; }
    if (teraz) wysokich++;
    probek++;
  }
  przywrocPiny();
  String j = "{\"zmian\":" + String(zmian) +
             ",\"procent_wysoko\":" + String((100.0 * wysokich) / probek, 1) +
             ",\"probek\":" + String(probek) + ",\"podciagniecie\":" + String(pod ? 1 : 0) + "}";
  http.send(200, "application/json", j);
}

// Test pinu: czy da sie go wysterowac w oba stany. Jesli pin nie potrafi
// przyjac stanu wysokiego, jest zwarty do masy na plytce.
String testPinu(uint8_t pin) {
  pinMode(pin, INPUT_PULLUP);
  delay(3);
  int gora = digitalRead(pin);
  pinMode(pin, INPUT_PULLDOWN);
  delay(3);
  int dol = digitalRead(pin);
  pinMode(pin, INPUT);
  String w;
  if (gora == 1 && dol == 0) w = "WOLNY (podaza za podciagnieciem)";
  else if (gora == 0 && dol == 0) w = "TRZYMANY NISKO";
  else if (gora == 1 && dol == 1) w = "TRZYMANY WYSOKO";
  else w = "dziwny";
  return w + " [pullup=" + String(gora) + " pulldown=" + String(dol) + "]";
}

void httpPin() {
  magistrala.end();
  String j = String("GPIO16 (RX2): ") + testPinu(16) +
             " | GPIO17 (TX2): " + testPinu(17) +
             " | GPIO4 (kierunek): " + testPinu(4);
  przywrocPiny();
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);    // MAX3485: NISKO = odbior
  http.send(200, "text/plain", j);
}

// Test wlasny ukladu magistrali: nadaj kilka bajtow i sprawdz, czy wrocily.
// Nadajnik i odbiornik siedza w jednej kosci, wiec przy wlaczonym nadawaniu
// odbiornik slyszy wlasna transmisje. Brak echa = kosc nie dziala.
void httpEcho() {
  String w = "";
  const uint8_t wzor[4] = {0x55, 0xAA, 0x0F, 0xF0};
  for (uint8_t faza = 0; faza < 2; faza++) {
    bool en = (faza == 1);
    magistrala.end();
    pinMode(PIN_DIR, OUTPUT);
    digitalWrite(PIN_DIR, en ? HIGH : LOW);
    delay(5);
    przywrocPiny();
    delay(5);
    while (magistrala.available()) magistrala.read();
    magistrala.write(wzor, 4);
    magistrala.flush();
    unsigned long doKiedy = millis() + 400;
    String odb = "";
    uint8_t n = 0;
    while (millis() < doKiedy) {
      while (magistrala.available()) { odb += String(magistrala.read(), HEX) + " "; n++; }
      delay(2);
    }
    w += String("kierunek ") + (en ? "WYSOKO (nadawanie)" : "NISKO (odbior)") +
         ": wroclo " + String(n) + " bajtow [" + odb + "]\n";
  }
  w += "wyslano: 55 aa f f0\n";
  digitalWrite(PIN_DIR, LOW);    // MAX3485: NISKO = odbior
  http.send(200, "text/plain", w);
}

// Nadawanie ciagle przez 20 s: pozwala zmierzyc miernikiem albo oscyloskopem,
// czy nadajnik ukladu magistrali w ogole wystawia sygnal na wyprowadzenia A i B.
void httpNadawaj() {
  http.send(200, "text/plain", "nadaje przez 90 s - mierz teraz miedzy A i B modulu");
  magistrala.end();
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, HIGH);
  delay(5);
  przywrocPiny();
  unsigned long doKiedy = millis() + 90000;
  while (millis() < doKiedy) {
    magistrala.write(0x55);
    magistrala.flush();
  }
  digitalWrite(PIN_DIR, LOW);    // MAX3485: NISKO = odbior
}

// Surowy podglad tego, co wchodzi z magistrali - do porownania z oczekiwanym
// naglowkiem ramki Gree (7E 7E FF 40 11 17 ...).
void httpKierunek() {
  int st = http.hasArg("stan") ? http.arg("stan").toInt() : -1;
  if (st == 0 || st == 1) { pinMode(PIN_DIR, OUTPUT); digitalWrite(PIN_DIR, st ? HIGH : LOW); }
  http.send(200, "text/plain", String("kierunek=") + digitalRead(PIN_DIR));
}

// Surowy przebieg z linii odbiorczej: dlugosci kolejnych odcinkow L/H w us,
// od pierwszego zbocza opadajacego po co najmniej 20 ms spoczynku.
static inline int czytRx() { return (REG_READ(GPIO_IN_REG) >> PIN_RX) & 1; }
void httpSurowe() {
  uint32_t t0 = millis();
  int lv = czytRx();
  uint32_t ostatnie = micros();
  while (millis() - t0 < 1500) {
    int p = czytRx();
    if (p != lv) { lv = p; ostatnie = micros(); }
    if (micros() - ostatnie > 20000) break;
  }
  t0 = millis();
  while (czytRx() == lv && millis() - t0 < 1500) {}
  static uint32_t zb[700];
  uint16_t n = 0;
  int poprz = czytRx();
  int pierwszy = poprz;
  uint32_t start = micros(), tp = start;
  while (micros() - start < 330000 && n < 700) {
    int p = czytRx();
    if (p != poprz) { uint32_t t = micros(); zb[n++] = t - tp; tp = t; poprz = p; }
  }
  String w = "odcinkow: " + String(n) + "  ";
  for (uint16_t i = 0; i < n; i++) { w += String(zb[i]); w += (((i & 1) ? !pierwszy : pierwszy) ? "H " : "L "); }
  http.send(200, "text/plain", w);
}

void httpMk() {
  if (http.hasArg("odwroc")) mkOdwroc = http.arg("odwroc").toInt() ? 1 : 0;
  noInterrupts();
  mkStan = 0; mkOkno = 0xFF; mkGlowa = 0; mkOgon = 0;
  mkStarty = 0; mkBajty = 0; mkBledyStopu = 0;
  interrupts();
  bufLen = 0;
  http.send(200, "text/plain", String("odwrocenie=") + mkOdwroc + ", liczniki wyzerowane");
}

void httpZrzut() {
  String h = "";
  uint16_t n = 0;
  unsigned long doKiedy = millis() + 4000;
  while (millis() < doKiedy && n < 220) {
    while (mkDostepny() && n < 220) {
      uint8_t b = mkCzytaj();
      if (b < 16) h += "0";
      h += String(b, HEX);
      h += " ";
      n++;
    }
    delay(2);
  }
  http.send(200, "text/plain", String("odebrano ") + n + " bajtow w 4 s: " + h);
}

// Procesor sam mierzy szerokosc najkrotszego impulsu na linii odbiorczej.
// Z niej wynika wprost predkosc transmisji magistrali.
void httpBity() {
  magistrala.end();
  pinMode(PIN_RX, INPUT);
  uint32_t min50 = 0xFFFFFFFF, min100 = 0xFFFFFFFF, min300 = 0xFFFFFFFF;
  uint32_t n = 0, ponad100 = 0, ponad300 = 0, ponad700 = 0;
  int poprz = digitalRead(PIN_RX);
  uint32_t tPoprz = micros();
  uint32_t koniec = millis() + 5000;
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
  }
  przywrocPiny();
  String w = "przelaczen: " + String(n);
  w += " | powyzej 100us: " + String(ponad100);
  w += " | powyzej 300us: " + String(ponad300);
  w += " | powyzej 700us: " + String(ponad700);
  w += " || najkrotszy >50us: " + (min50 == 0xFFFFFFFF ? String("-") : String(min50));
  w += " | >100us: " + (min100 == 0xFFFFFFFF ? String("-") : String(min100));
  w += " | >300us: " + (min300 == 0xFFFFFFFF ? String("-") : String(min300));
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
  j += ",\"mk_starty\":" + String(mkStarty);
  j += ",\"mk_bajty\":" + String(mkBajty);
  j += ",\"mk_bledy_stopu\":" + String(mkBledyStopu);
  j += ",\"temp_procesora_c\":" + String(temperatureRead(), 1);
  j += ",\"mk_odwroc\":" + String(mkOdwroc);
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
  j += ",\"skan_wynik\":\"" + String(wybranyWariant >= 0 ? WARIANTY[wybranyWariant].opis : "cisza we wszystkich wariantach") + "\"";
  j += ",\"skan_bajty\":\"" + String(skanBajtow[0]) + "/" + String(skanBajtow[1]) + "/" + String(skanBajtow[4]) +
       "/" + String(skanBajtow[5]) + "/" + String(skanBajtow[2]) + "/" + String(skanBajtow[3]) + "/" + String(skanBajtow[6]) + "/" + String(skanBajtow[7]) + "\"";
  { String sz = ""; for (uint8_t i = 0; i < 8; i++) { if (i) sz += "/"; sz += String(skanZnacznikow[i]); }
    j += ",\"znaczniki_7E\":\"" + sz + "\""; }
  j += ",\"modul\":\"" + String(NAZWA_OTA) + "\"";
  j += ",\"wolna_pamiec\":" + String(ESP.getFreeHeap());
  j += ",\"min_wolna_pamiec\":" + String(minWolnejPamieci);
  j += ",\"uptime_s\":" + String(millis() / 1000);
  j += "}";
  http.send(200, "application/json", j);
}

void httpUstaw() {
  przejmijZamiar();   // gdyby komenda przyszla przed pierwsza ramka - nic nie robi
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

// Samodzielna diagnoza polaczen wokol modulu RS485. Procesor wymusza stan na
// pinie nadawczym (DI modulu) i na pinie kierunku (DE), a czyta pin odbiorczy
// (RO modulu). Bez magistrali:
//  - kierunek NISKO: RO nie ma prawa podazac za DI. Jesli podaza -> mostek
//    miedzy sieciami RX2/TX2 (albo DE nie jest sterowane przez GPIO4).
//  - kierunek WYSOKO: nadajnik wlaczony, DI -> A/B -> odbiornik -> RO, wiec
//    RO MUSI podazac za DI (petla zwrotna). Nie podaza -> odbiornik wylaczony
//    (drut RE) albo modul bez zasilania.
//  - RO z podciaganiem w obie strony przy wolnym DI: [1,0] = RO nie steruje
//    (odbiornik wylaczony), [x,x] = RO steruje i taki jest jego spoczynek.
static int czytajZ(uint8_t pin, uint8_t tryb) { pinMode(pin, tryb); delay(3); return digitalRead(pin); }
void httpDiag() {
  magistrala.end();
  pinMode(PIN_DIR, OUTPUT); digitalWrite(PIN_DIR, LOW); delay(3);
  pinMode(PIN_RX, INPUT);
  pinMode(PIN_TX, OUTPUT);
  digitalWrite(PIN_TX, LOW);  delay(3); int a0 = digitalRead(PIN_RX);
  digitalWrite(PIN_TX, HIGH); delay(3); int a1 = digitalRead(PIN_RX);
  digitalWrite(PIN_DIR, HIGH); delay(3);
  digitalWrite(PIN_TX, LOW);  delay(3); int b0 = digitalRead(PIN_RX);
  digitalWrite(PIN_TX, HIGH); delay(3); int b1 = digitalRead(PIN_RX);
  digitalWrite(PIN_DIR, LOW); delay(3);
  pinMode(PIN_TX, INPUT);
  int cUp = czytajZ(PIN_RX, INPUT_PULLUP), cDn = czytajZ(PIN_RX, INPUT_PULLDOWN);
  pinMode(PIN_RX, INPUT);
  int dUp = czytajZ(PIN_TX, INPUT_PULLUP), dDn = czytajZ(PIN_TX, INPUT_PULLDOWN);
  pinMode(PIN_TX, INPUT);
  int eUp = czytajZ(PIN_DIR, INPUT_PULLUP), eDn = czytajZ(PIN_DIR, INPUT_PULLDOWN);
  // 6. DE nisko, DI tylko slabo podciagane: RO podaza => nadajnik wlaczony mimo DE nisko
  pinMode(PIN_DIR, OUTPUT); digitalWrite(PIN_DIR, LOW); delay(3);
  pinMode(PIN_RX, INPUT);
  pinMode(PIN_TX, INPUT_PULLUP);   delay(5); int fUp = digitalRead(PIN_RX);
  pinMode(PIN_TX, INPUT_PULLDOWN); delay(5); int fDn = digitalRead(PIN_RX);
  pinMode(PIN_TX, INPUT);
  przywrocPiny();
  String w;
  w += "1. kierunek NISKO, DI=0 -> RO=" + String(a0) + "; DI=1 -> RO=" + String(a1) +
       (a0 != a1 ? "   => RO PODAZA ZA DI PRZY WYLACZONYM NADAJNIKU: mostek RX2/TX2 albo DE nie sluch GPIO4" : "   (ok: nie podaza)") + "\n";
  w += "2. kierunek WYSOKO, DI=0 -> RO=" + String(b0) + "; DI=1 -> RO=" + String(b1) +
       (b0 != b1 ? "   (ok: petla zwrotna dziala = modul zasilany, nadajnik i odbiornik wlaczone)" : "   => BRAK PETLI ZWROTNEJ: odbiornik wylaczony (drut RE) albo nadajnik nie wlacza sie") + "\n";
  w += "3. RO przy wolnym DI: pullup=" + String(cUp) + " pulldown=" + String(cDn) +
       (cUp == 1 && cDn == 0 ? "   => RO NIE STERUJE (odbiornik wylaczony)" : (cUp == cDn ? "   (ok: RO steruje, spoczynek bez magistrali = " + String(cUp) + ")" : "   (dziwne)")) + "\n";
  w += "4. DI przy wolnym RO: pullup=" + String(dUp) + " pulldown=" + String(dDn) +
       (dUp == 1 && dDn == 0 ? "   (ok: DI wolne)" : "   => cos trzyma DI: mostek albo rezystor na module") + "\n";
  w += "5. DE (GPIO4) jako wejscie: pullup=" + String(eUp) + " pulldown=" + String(eDn) +
       (eUp == 0 && eDn == 0 ? "   (modul ma rezystor sciagajacy EN do masy, jak w module 1)" : (eUp == 1 && eDn == 0 ? "   (EN wolne: brak rezystora albo brak przewodu do EN)" : "   => EN trzymane wysoko: nadajnik STALE wlaczony!")) + "\n";
  w += "6. kierunek NISKO, DI tylko slabo podciagane: DI^=1 -> RO=" + String(fUp) + "; DIv=0 -> RO=" + String(fDn) +
       (fUp != fDn ? "   => NADAJNIK WLACZONY MIMO DE NISKO: modul nadaje bez przerwy i zakloca magistrale!" : "   (ok: nadajnik wylaczony)") + "\n";
  http.send(200, "text/plain", w);
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
// ── diagnostyka magistrali ─────────────────────────────────
// Cisza na magistrali ma dwie typowe przyczyny: zamienione RXD/TXD na module
// RS485 albo odwrotna polaryzacja sygnalu kierunku. Piny UART w ESP32 sa
// przypisywalne programowo, wiec obie da sie sprawdzic bez lutownicy.

void ustawWariant(uint8_t i) {
  magistrala.end();
  digitalWrite(PIN_DIR, WARIANTY[i].en ? HIGH : LOW);
  delay(5);
  magistrala.begin(1200, SERIAL_8N1, WARIANTY[i].rx, WARIANTY[i].tx, WARIANTY[i].inv);
}

void skanujMagistrale() {
  emit("[SKAN] szukam wariantu podlaczenia, 6 s na kazdy z osmiu...\n");
  for (uint8_t i = 0; i < 8; i++) {
    ustawWariant(i);
    while (magistrala.available()) magistrala.read();
    unsigned long doKiedy = millis() + 6000;
    uint16_t n = 0;
    while (millis() < doKiedy) {
      while (magistrala.available()) { if (magistrala.read() == 0x7E) skanZnacznikow[i]++; n++; }
      ArduinoOTA.handle();
      http.handleClient();
      delay(2);
    }
    skanBajtow[i] = n;
    emit("[SKAN] " + String(i) + ". " + String(WARIANTY[i].opis) +
         " -> " + String(n) + " bajtow\n");
  }
  uint8_t best = 0;
  for (uint8_t i = 1; i < 8; i++) if (skanZnacznikow[i] > skanZnacznikow[best]) best = i;
  wybranyWariant = (skanZnacznikow[best] > 0) ? (int8_t)best : -1;
  ustawWariant(best);
  if (wybranyWariant >= 0)
    emit("[SKAN] DZIALA: " + String(WARIANTY[best].opis) + "\n");
  else
    emit("[SKAN] cisza we wszystkich osmiu - sygnal nie dociera do modulu\n");
}

void setup() {
  pinMode(PIN_LED_STAN, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);    // MAX3485: NISKO = odbior           // domyślnie odbiór — na magistralę nie nadajemy
  Serial.begin(115200);

  // Port sprzetowy UART2 nie jest uzywany: odbior robi miekki odbiornik na
  // PIN_RX, a nadawania po RS485 nie ma. Pin nadawczy zostaje wejsciem na
  // stale - gdyby byl wyjsciem, na plytce z mostkiem RX2-TX2 nadpisywalby
  // wyjscie odbiornika modulu.
  pinMode(PIN_RX, INPUT);
  pinMode(PIN_TX, INPUT);

  bool wczytane = czytajNastawy();

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                 // stabilniejszy odbiór przy ciągłym nasłuchu
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  telnet.begin();

  http.on("/stan", httpStan);
  http.on("/linia", httpLinia);
  http.on("/pin", httpPin);
  http.on("/zrzut", httpZrzut);
  http.on("/mk", httpMk);
  http.on("/kierunek", httpKierunek);
  http.on("/surowe", httpSurowe);
  http.on("/bity", httpBity);
  http.on("/ustaw", httpUstaw);
  http.on("/diag", httpDiag);
  http.on("/", httpStrona);
  http.begin();

  klima.begin();

  ArduinoOTA.setHostname(NAZWA_OTA);
  ArduinoOTA.onStart([]() { esp_task_wdt_delete(NULL); });   // wgrywanie blokuje petle
  ArduinoOTA.onError([](ota_error_t) { esp_task_wdt_add(NULL); });
  ArduinoOTA.begin();

  // Straznik zawieszenia: petla glowna musi zglaszac sie co najmniej raz na 90 s,
  // inaczej procesor restartuje sie sam. Modul wisi pod sufitem - zawieszenie bez
  // restartu oznacza drabine. 90 s, bo najdluzsza diagnostyka (/bity, /zrzut)
  // blokuje petle na 5 s, a wgrywanie po WiFi jest wylaczone ze straznika osobno.
  esp_task_wdt_config_t straznik = { .timeout_ms = 90000, .idle_core_mask = 0, .trigger_panic = true };
  if (esp_task_wdt_reconfigure(&straznik) != ESP_OK) esp_task_wdt_init(&straznik);
  esp_task_wdt_add(NULL);

  startMs = millis();
  ostatniBajtMs = millis();
  emit("\n=== MODUL v2 (" + String(NAZWA_OTA) + ") — ESP32, UART2 sprzetowy ===\n");
  uruchomMiekkiOdbiornik();
  emit(wczytane ? "[NASTAWY] wczytane z pamieci\n" : "[NASTAWY] pamiec pusta — wartosci domyslne\n");
}

// ── pętla główna: nic jej nie blokuje ─────────────────────────────────────
// Dioda na plytce: miga szybko gdy szuka sieci, wolno gdy polaczona.
// Brak migania = procesor nie wykonuje programu.
void migajStanem() {
  static unsigned long ledMs = 0;
  static bool ledStan = false;
  unsigned long okres;
  if (millis() - ostatniBajtMs < 600) okres = 60;          // dane z magistrali: szybkie migotanie
  else okres = (WiFi.status() == WL_CONNECTED) ? 1500 : 150;
  if (millis() - ledMs >= okres) {
    ledMs = millis();
    ledStan = !ledStan;
    digitalWrite(PIN_LED_STAN, ledStan);
  }
}

void loop() {
  esp_task_wdt_reset();
  migajStanem();
  ArduinoOTA.handle();
  http.handleClient();

  odbieraj();
  obsluzWeryfikacje();


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
