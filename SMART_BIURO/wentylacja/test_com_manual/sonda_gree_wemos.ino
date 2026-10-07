/*
 * SONDA MAGISTRALI COM-MANUAL - wersja na WeMos D1 (ESP8266)
 * ==========================================================
 * Plytka: WeMos D1 R1 (ESP8266MOD). W Arduino IDE:
 *   - zainstaluj pakiet "esp8266" (Boards Manager),
 *   - wybierz plytke: "LOLIN(WEMOS) D1 R1",
 *   - monitor szeregowy: 115200.
 *
 * Polaczenia (wg schemat_sondy_WEMOS_D1.png):
 *   D6 (GPIO12) -> DI      D5 (GPIO14) <- RO przez dzielnik 1k/2k (5V->3,3V!)
 *   D7 (GPIO13) -> DE+RE   5V -> VCC MAX485, GND wspolne z GND COM-MANUAL
 *   A/B modulu -> A/B gniazda. Pin +12V gniazda ZOSTAJE WOLNY.
 *
 * Dziala tak samo jak wersja UNO: 20 s nasluchu, potem sonda co 3 s.
 * Odpowiedz jednostki = ramka 7E 7E FF ... -> duzy komunikat SUKCESU.
 *
 * Po tescie: odlacz sonde i wylacz/wlacz bezpiecznik klimatyzatora
 * (jednostka moze zmienic nastawy i ignorowac pilota IR po ramkach sondy).
 */

#include <SoftwareSerial.h>   // na ESP8266 to EspSoftwareSerial z pakietu core

const uint8_t PIN_RX  = 14;   // D5  <- RO (przez dzielnik!)
const uint8_t PIN_TX  = 12;   // D6  -> DI
const uint8_t PIN_DIR = 13;   // D7  -> DE+RE

SoftwareSerial gree;

const uint8_t PROBE[] = {
  0x7E, 0x7E, 0x00, 0xFF, 0x11, 0x0E,
  0x00, 0x00, 0x02, 0x01, 0x89, 0x8A, 0xBE, 0x47,
  0x00, 0x80, 0x00, 0x00, 0x00, 0x99
};

const unsigned long FAZA_NASLUCHU_MS = 20000UL;
const unsigned long ODSTEP_SONDY_MS  = 3000UL;

unsigned long startMs = 0, ostatniaSonda = 0, ostatniBajt = 0;
uint8_t buf[64];
uint8_t bufLen = 0;

void hex2(uint8_t b) {
  if (b < 0x10) Serial.print('0');
  Serial.print(b, HEX);
  Serial.print(' ');
}

void wyslijSonde() {
  Serial.print(F("\n[TX "));
  Serial.print(millis() / 1000.0, 1);
  Serial.print(F("s] wysylam sonde: "));
  for (uint8_t i = 0; i < sizeof(PROBE); i++) hex2(PROBE[i]);
  Serial.println();

  digitalWrite(PIN_DIR, HIGH);
  delayMicroseconds(100);
  gree.write(PROBE, sizeof(PROBE));
  gree.flush();                 // czekaj na koniec nadawania
  digitalWrite(PIN_DIR, LOW);
}

void analizujBufor() {
  while (bufLen >= 6) {
    if (buf[0] != 0x7E || buf[1] != 0x7E) {
      memmove(buf, buf + 1, --bufLen);
      continue;
    }
    uint8_t dlBody = buf[5];
    uint8_t total  = 6 + dlBody;
    if (total > sizeof(buf)) { memmove(buf, buf + 2, bufLen -= 2); continue; }
    if (bufLen < total) return;

    uint8_t x = 0;
    for (uint8_t i = 0; i < total - 1; i++) x ^= buf[i];
    bool sumaOK = (x == buf[total - 1]);

    Serial.print(F("\n>>> RAMKA ("));
    Serial.print(sumaOK ? F("SUMA OK") : F("suma bledna"));
    Serial.print(F("): "));
    for (uint8_t i = 0; i < total; i++) hex2(buf[i]);
    Serial.println();

    if (buf[2] == 0xFF) {
      Serial.println(F("*********************************************"));
      Serial.println(F("***  ODPOWIEDZ JEDNOSTKI - KOMUNIKACJA OK ***"));
      Serial.println(F("*********************************************"));
    }
    memmove(buf, buf + total, bufLen -= total);
  }
}

void setup() {
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, LOW);
  Serial.begin(115200);
  gree.begin(1200, SWSERIAL_8N1, PIN_RX, PIN_TX);
  startMs = millis();
  Serial.println();
  Serial.println(F("=== SONDA COM-MANUAL / Gree GKH (WeMos D1) ==="));
  Serial.println(F("Faza 1: 20 s czystego nasluchu..."));
}

void loop() {
  while (gree.available()) {
    uint8_t b = gree.read();
    if (millis() - ostatniBajt > 200) Serial.print(F("\n[RX] "));
    ostatniBajt = millis();
    hex2(b);
    if (bufLen < sizeof(buf)) buf[bufLen++] = b;
    analizujBufor();
  }

  if (millis() - startMs > FAZA_NASLUCHU_MS &&
      millis() - ostatniaSonda > ODSTEP_SONDY_MS) {
    ostatniaSonda = millis();
    wyslijSonde();
  }
  yield();   // ESP8266: nie glodzimy WiFi/watchdoga
}
