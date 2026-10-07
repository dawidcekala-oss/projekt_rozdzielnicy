/*
 * SONDA COM-MANUAL v2 (WiFi) - WeMos D1 / ESP8266
 * ================================================
 * Jak v1, ale log dostepny zdalnie:
 *  - laczy sie z WiFi (2.4 GHz),
 *  - co 2 s rozglasza UDP na porcie 4210: "SONDA-GREE <ip>",
 *  - serwer TCP na porcie 23 (telnet): po polaczeniu wysyla historie
 *    logu i streamuje na zywo,
 *  - USB/Serial dziala rownolegle jako zapas.
 * Zasilanie w terenie: powerbank / ladowarka (kabel bez danych wystarczy).
 */

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <SoftwareSerial.h>

const char* WIFI_SSID = "AmperePoint";
const char* WIFI_PASS = "starwars77";

const uint8_t PIN_RX  = 14;   // D5  <- TXD bramki (przez dzielnik)
const uint8_t PIN_TX  = 12;   // D6  -> RXD bramki
const uint8_t PIN_DIR = 13;   // D7  (przy bramce nieuzywane)

SoftwareSerial gree;
WiFiServer server(23);
WiFiClient client;
WiFiUDP udp;

const uint8_t PROBE[] = {
  0x7E, 0x7E, 0x00, 0xFF, 0x11, 0x0E,
  0x00, 0x00, 0x02, 0x01, 0x89, 0x8A, 0xBE, 0x47,
  0x00, 0x80, 0x00, 0x00, 0x00, 0x99
};

const unsigned long FAZA_NASLUCHU_MS = 20000UL;
const unsigned long ODSTEP_SONDY_MS  = 3000UL;
const unsigned long ODSTEP_BEACON_MS = 2000UL;

unsigned long startMs = 0, ostatniaSonda = 0, ostatniBajt = 0, ostatniBeacon = 0;
uint8_t buf[64];
uint8_t bufLen = 0;
String ring;
const unsigned int RING_MAX = 4000;
bool wifiBylo = false;

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

void wyslijSonde() {
  String s = "\n[TX " + String(millis() / 1000.0, 1) + "s] sonda: ";
  for (uint8_t i = 0; i < sizeof(PROBE); i++) s += hex2(PROBE[i]);
  emit(s + "\n");
  digitalWrite(PIN_DIR, HIGH);
  delayMicroseconds(100);
  gree.write(PROBE, sizeof(PROBE));
  gree.flush();
  digitalWrite(PIN_DIR, LOW);
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

    if (buf[2] == 0xFF) {
      emit("*********************************************\n");
      emit("***  ODPOWIEDZ JEDNOSTKI - KOMUNIKACJA OK ***\n");
      emit("*********************************************\n");
    }
    memmove(buf, buf + total, bufLen -= total);
  }
}

void setup() {
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);
  Serial.begin(115200);
  gree.begin(1200, SWSERIAL_8N1, PIN_RX, PIN_TX);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  server.begin();
  startMs = millis();
  emit("\n=== SONDA COM-MANUAL v2 (WiFi) ===\n");
  emit("Lacze z siecia: " + String(WIFI_SSID) + "...\n");
  emit("Faza 1: 20 s czystego nasluchu magistrali...\n");
}

void loop() {
  // WiFi - meldunek po polaczeniu
  if (WiFi.status() == WL_CONNECTED && !wifiBylo) {
    wifiBylo = true;
    emit("[WiFi] POLACZONO, IP: " + WiFi.localIP().toString() + "\n");
  }
  if (WiFi.status() != WL_CONNECTED && wifiBylo) {
    wifiBylo = false;
    emit("[WiFi] utracono polaczenie, wznawiam...\n");
  }

  // beacon UDP
  if (wifiBylo && millis() - ostatniBeacon > ODSTEP_BEACON_MS) {
    ostatniBeacon = millis();
    IPAddress ip = WiFi.localIP(), m = WiFi.subnetMask(), b;
    for (int i = 0; i < 4; i++) b[i] = ip[i] | ~m[i];
    udp.beginPacket(b, 4210);
    udp.print("SONDA-GREE " + ip.toString());
    udp.endPacket();
  }

  // klient telnet
  if (server.hasClient()) {
    if (client) client.stop();
    client = server.accept();
    client.print("=== SONDA GREE - polaczono zdalnie ===\n--- HISTORIA ---\n");
    client.print(ring);
    client.print("\n--- NA ZYWO ---\n");
  }

  // odbior z magistrali
  while (gree.available()) {
    uint8_t bb = gree.read();
    if (millis() - ostatniBajt > 200) emit("\n[RX] ");
    ostatniBajt = millis();
    emit(hex2(bb));
    if (bufLen < sizeof(buf)) buf[bufLen++] = bb;
    analizujBufor();
  }

  // sondowanie
  if (millis() - startMs > FAZA_NASLUCHU_MS &&
      millis() - ostatniaSonda > ODSTEP_SONDY_MS) {
    ostatniaSonda = millis();
    wyslijSonde();
  }
  yield();
}
