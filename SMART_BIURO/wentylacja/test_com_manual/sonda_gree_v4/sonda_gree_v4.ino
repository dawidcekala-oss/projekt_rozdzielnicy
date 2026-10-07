/*
 * SONDA COM-MANUAL v3 - zdalnie programowalne zapytania (Faza 2 dekodowania)
 * ==========================================================================
 * Jak v2 (WiFi, beacon UDP 4210, telnet 23 z historia i streamem), plus:
 * komendy tekstowe przychodzace od klienta telnet (linia zakonczona \n):
 *
 *   TX <hex ...>    wyslij dokladnie te bajty, jednorazowo
 *   TXX <hex ...>   wyslij te bajty + dolacz na koncu sume XOR (liczona z calosci)
 *   SET <hex ...>   ustaw nowa ramke okresowa (dokladnie te bajty)
 *   SETX <hex ...>  jw., ale z auto-XOR przy kazdej wysylce
 *   STOP            wstrzymaj wysylanie okresowe
 *   START           wznow wysylanie okresowe
 *   T <ms>          zmien odstep okresowy (500..60000 ms)
 *   INFO            wypisz aktualna konfiguracje
 *
 * Polaczenia elektryczne bez zmian (bramka GRZ47-G):
 *   D6=GPIO12 -> "TXD" CN2, "RXD" CN2 -> dzielnik -> D5=GPIO14,
 *   D7=GPIO13 -> TXP (klucz nadawania), RXP -> GND na stale.
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <SoftwareSerial.h>

const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";

const uint8_t PIN_RX  = 14;   // D5  <- "RXD" bramki (przez dzielnik)
const uint8_t PIN_TX  = 12;   // D6  -> "TXD" bramki
const uint8_t PIN_DIR = 13;   // D7  -> TXP (klucz nadawania)

SoftwareSerial gree;
WiFiServer server(23);
WiFiClient client;
WiFiUDP udp;

// domyslna ramka okresowa = znane zapytanie o stan rzeczywisty
uint8_t ramkaOkresowa[48] = {
  0x7E, 0x7E, 0x00, 0xFF, 0x11, 0x0E,
  0x00, 0x00, 0x02, 0x01, 0x89, 0x8A, 0xBE, 0x47,
  0x00, 0x80, 0x00, 0x00, 0x00, 0x99
};
uint8_t dlOkresowa = 20;
bool autoXorOkresowa = false;
bool okresoweWl = true;
unsigned long odstepMs = 3000UL;

const unsigned long FAZA_NASLUCHU_MS = 8000UL;
const unsigned long ODSTEP_BEACON_MS = 2000UL;

unsigned long startMs = 0, ostatniaSonda = 0, ostatniBajt = 0, ostatniBeacon = 0;
uint8_t buf[64];
uint8_t bufLen = 0;
String ring;
const unsigned int RING_MAX = 4000;
bool wifiBylo = false;
String liniaCmd;

void emit(const String& s) {
  Serial.print(s);
  ring += s;
  if (ring.length() > RING_MAX) ring.remove(0, ring.length() - RING_MAX);
  if (client && client.connected()) client.print(s);
}

String hex2(uint8_t b) {
  String s = String(b, HEX);
  if (s.length() < 2) s = "0" + s;
  s.toUpperCase();
  return s + " ";
}

// --- parametry nadawania (zmienne komendami) ---
bool intTxWl = false;        // przerwania podczas nadawania (false = precyzyjne bity)
unsigned int trzymajDeMs = 3;  // ile ms trzymac klucz nadawania po ostatnim bajcie
unsigned int czekajPoRx = 0;   // >0: nadawaj dopiero N ms po ostatnim odebranym bajcie
uint8_t powtorzen = 1;         // ile razy powtorzyc ramke

void wyslijRaz(uint8_t* robocza, uint8_t total) {
  digitalWrite(PIN_DIR, HIGH);
  delayMicroseconds(200);
  gree.write(robocza, total);
  gree.flush();
  delay(trzymajDeMs);
  digitalWrite(PIN_DIR, LOW);
}

void wyslijBajty(const uint8_t* dane, uint8_t n, bool autoXor, const char* etyk) {
  uint8_t robocza[50];
  memcpy(robocza, dane, n);
  uint8_t total = n;
  if (autoXor && total < 49) {
    uint8_t x = 0;
    for (uint8_t i = 0; i < total; i++) x ^= robocza[i];
    robocza[total++] = x;
  }
  String s = "\n[" + String(etyk) + " " + String(millis() / 1000.0, 1) + "s] ";
  for (uint8_t i = 0; i < total; i++) s += hex2(robocza[i]);
  emit(s + "\n");

  for (uint8_t p = 0; p < powtorzen; p++) {
    if (czekajPoRx > 0) {
      // synchronizacja: czekaj az magistrala ucichnie na czekajPoRx ms
      unsigned long limit = millis() + 3000;
      while (millis() < limit) {
        while (gree.available()) {   // odbieraj w trakcie czekania
          uint8_t bb = gree.read();
          if (millis() - ostatniBajt > 200) emit("\n[RX t=" + String(millis()) + "] ");
          ostatniBajt = millis();
          emit(hex2(bb));
          if (bufLen < sizeof(buf)) buf[bufLen++] = bb;
          analizujBufor();
        }
        if (millis() - ostatniBajt >= czekajPoRx) break;
        yield();
      }
    }
    wyslijRaz(robocza, total);
    if (p + 1 < powtorzen) delay(40);
  }
}

void analizujBufor() {
  while (bufLen >= 6) {
    if (buf[0] != 0x7E || buf[1] != 0x7E) { memmove(buf, buf + 1, --bufLen); continue; }
    uint8_t dlBody = buf[5];
    uint8_t total  = 6 + dlBody;
    if (total > sizeof(buf)) { memmove(buf, buf + 2, bufLen -= 2); continue; }
    if (bufLen < total) return;
    uint8_t x = 0;
    for (uint8_t i = 0; i < total - 1; i++) x ^= buf[i];
    bool sumaOK = (x == buf[total - 1]);
    String s = "\n>>> RAMKA (";
    s += sumaOK ? "SUMA OK" : "suma bledna";
    s += "): ";
    for (uint8_t i = 0; i < total; i++) s += hex2(buf[i]);
    emit(s + "\n");
    memmove(buf, buf + total, bufLen -= total);
  }
}

int parsujHex(const String& linia, int od, uint8_t* wy, int maxN) {
  int n = 0;
  int i = od;
  while (i < (int)linia.length() && n < maxN) {
    while (i < (int)linia.length() && linia[i] == ' ') i++;
    if (i >= (int)linia.length()) break;
    int j = i;
    while (j < (int)linia.length() && linia[j] != ' ') j++;
    String tok = linia.substring(i, j);
    tok.trim();
    if (tok.length() == 0) { i = j; continue; }
    char* koniec;
    long v = strtol(tok.c_str(), &koniec, 16);
    if (*koniec != 0 || v < 0 || v > 255) return -1;
    wy[n++] = (uint8_t)v;
    i = j;
  }
  return n;
}

void obsluzKomende(String linia) {
  linia.trim();
  if (linia.length() == 0) return;
  String duza = linia;
  duza.toUpperCase();
  uint8_t tmp[48];

  if (duza == "STOP") { okresoweWl = false; emit("[CMD] okresowe: STOP\n"); return; }
  if (duza == "START") { okresoweWl = true; emit("[CMD] okresowe: START\n"); return; }
  if (duza == "INFO") {
    String s = "[CMD] okres=" + String(odstepMs) + "ms, wl=" + String(okresoweWl ? 1 : 0)
             + ", autoXor=" + String(autoXorOkresowa ? 1 : 0)
             + ", intTx=" + String(intTxWl ? 1 : 0)
             + ", deHold=" + String(trzymajDeMs) + "ms"
             + ", poRx=" + String(czekajPoRx) + "ms"
             + ", powt=" + String(powtorzen) + ", ramka: ";
    for (uint8_t i = 0; i < dlOkresowa; i++) s += hex2(ramkaOkresowa[i]);
    emit(s + "\n");
    return;
  }
  if (duza.startsWith("INTTX ")) {
    intTxWl = (duza.substring(6).toInt() != 0);
    gree.enableIntTx(intTxWl);
    emit("[CMD] intTx=" + String(intTxWl ? 1 : 0) + "\n");
    return;
  }
  if (duza.startsWith("DEHOLD ")) {
    long v = duza.substring(7).toInt();
    if (v >= 0 && v <= 200) { trzymajDeMs = v; emit("[CMD] deHold=" + String(v) + "ms\n"); }
    return;
  }
  if (duza.startsWith("PORX ")) {
    long v = duza.substring(5).toInt();
    if (v >= 0 && v <= 2000) { czekajPoRx = v; emit("[CMD] poRx=" + String(v) + "ms\n"); }
    return;
  }
  if (duza.startsWith("POWT ")) {
    long v = duza.substring(5).toInt();
    if (v >= 1 && v <= 20) { powtorzen = v; emit("[CMD] powt=" + String(v) + "\n"); }
    return;
  }
  if (duza.startsWith("T ")) {
    long v = duza.substring(2).toInt();
    if (v >= 500 && v <= 60000) { odstepMs = v; emit("[CMD] okres=" + String(v) + "ms\n"); }
    else emit("[CMD] BLAD: T 500..60000\n");
    return;
  }
  bool autoX = false;
  int od = -1;
  const char* etyk = "TX-CMD";
  if (duza.startsWith("TXX ")) { autoX = true; od = 4; }
  else if (duza.startsWith("TX ")) { od = 3; }
  else if (duza.startsWith("SETX ") || duza.startsWith("SET ")) {
    bool ax = duza.startsWith("SETX ");
    int o = ax ? 5 : 4;
    int n = parsujHex(duza, o, tmp, sizeof(tmp));
    if (n <= 0) { emit("[CMD] BLAD: zle bajty w SET\n"); return; }
    memcpy(ramkaOkresowa, tmp, n);
    dlOkresowa = n;
    autoXorOkresowa = ax;
    emit("[CMD] nowa ramka okresowa (" + String(n) + " B, autoXor=" + String(ax ? 1 : 0) + ")\n");
    return;
  }
  if (od > 0) {
    int n = parsujHex(duza, od, tmp, sizeof(tmp));
    if (n <= 0) { emit("[CMD] BLAD: zle bajty w TX\n"); return; }
    wyslijBajty(tmp, n, autoX, etyk);
    return;
  }
  emit("[CMD] nieznana komenda: " + linia + "\n");
}

void setup() {
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);
  Serial.begin(115200);
  gree.begin(1200, SWSERIAL_8N1, PIN_RX, PIN_TX);
  gree.enableIntTx(intTxWl);   // domyslnie false = bity nadawane bez zaklocen od WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  server.begin();
  ArduinoOTA.setHostname("sonda-gree");
  ArduinoOTA.begin();
  startMs = millis();
  emit("\n=== SONDA v4 (precyzyjne nadawanie + OTA) ===\n");
}

void loop() {
  ArduinoOTA.handle();
  if (WiFi.status() == WL_CONNECTED && !wifiBylo) {
    wifiBylo = true;
    emit("[WiFi] POLACZONO, IP: " + WiFi.localIP().toString() + "\n");
  }
  if (WiFi.status() != WL_CONNECTED && wifiBylo) {
    wifiBylo = false;
    emit("[WiFi] utracono polaczenie, wznawiam...\n");
  }

  if (wifiBylo && millis() - ostatniBeacon > ODSTEP_BEACON_MS) {
    ostatniBeacon = millis();
    IPAddress ip = WiFi.localIP(), m = WiFi.subnetMask(), b;
    for (int i = 0; i < 4; i++) b[i] = ip[i] | ~m[i];
    udp.beginPacket(b, 4210);
    udp.print("SONDA-GREE " + ip.toString());
    udp.endPacket();
  }

  if (server.hasClient()) {
    if (client) client.stop();
    client = server.accept();
    liniaCmd = "";
    client.print("=== SONDA v3 - polaczono ===\n--- HISTORIA ---\n");
    client.print(ring);
    client.print("\n--- NA ZYWO ---\n");
  }

  // komendy od klienta telnet
  while (client && client.connected() && client.available()) {
    char c = client.read();
    if (c == '\n') { obsluzKomende(liniaCmd); liniaCmd = ""; }
    else if (c != '\r' && liniaCmd.length() < 200) liniaCmd += c;
  }

  // odbior z magistrali
  while (gree.available()) {
    uint8_t bb = gree.read();
    if (millis() - ostatniBajt > 200) emit("\n[RX t=" + String(millis()) + "] ");
    ostatniBajt = millis();
    emit(hex2(bb));
    if (bufLen < sizeof(buf)) buf[bufLen++] = bb;
    analizujBufor();
  }

  // wysylka okresowa
  if (okresoweWl && millis() - startMs > FAZA_NASLUCHU_MS &&
      millis() - ostatniaSonda > odstepMs) {
    ostatniaSonda = millis();
    wyslijBajty(ramkaOkresowa, dlOkresowa, autoXorOkresowa, "TX");
  }
  yield();
}
