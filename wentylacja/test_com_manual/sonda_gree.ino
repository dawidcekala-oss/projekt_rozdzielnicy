/*
 * SONDA MAGISTRALI COM-MANUAL (Gree GKH / plyta GRZ4M-A3)
 * =======================================================
 * Cel: sprawdzic, czy klimatyzator odpowiada na ramki protokolu
 * sterownika przewodowego (dokumentacja: github.com/maxim-smirnov/gree-wired-proto).
 *
 * Sprzet: Arduino UNO + modul MAX485 (wg schematu schemat_sondy_COM-MANUAL.png)
 *   D3 -> DI, D2 <- RO, D4 -> DE+RE (zmostkowane), 5V -> VCC, GND wspolne.
 *   A/B modulu -> A/B gniazda COM-MANUAL. Pinu +12V NIE podlaczamy.
 *
 * Dzialanie:
 *   Faza 1 (pierwsze 20 s): tylko nasluch - moze jednostka sama cos nadaje.
 *   Faza 2: co 3 s wysylana jest przykladowa ramka "sterownik -> jednostka"
 *           z dokumentacji protokolu, dalej nasluch.
 *   Wszystko, co przyjdzie, jest wypisywane HEX-em na Serial Monitor (115200).
 *   Ramka zaczynajaca sie od 7E 7E FF ... = ODPOWIEDZ JEDNOSTKI = SUKCES.
 *
 * UWAGI:
 *   - Ramka sondy niesie przykladowy stan nastaw - jednostka moze zmienic
 *     tryb/temperature albo przestac reagowac na pilota IR (mysli, ze ma
 *     sterownik przewodowy). Po tescie wylacz i wlacz bezpiecznik.
 *   - Brak odpowiedzi? Zamien przewody A i B (to bezpieczne) i sprobuj ponownie.
 */

#include <SoftwareSerial.h>

const uint8_t PIN_RX  = 2;   // RO modulu MAX485
const uint8_t PIN_TX  = 3;   // DI modulu MAX485
const uint8_t PIN_DIR = 4;   // DE+RE (HIGH = nadawanie)

SoftwareSerial gree(PIN_RX, PIN_TX);  // 8N1 (domyslne)

// Przykladowa ramka "remote -> unit" z gree-wired-proto:
const uint8_t PROBE[] = {
  0x7E, 0x7E, 0x00, 0xFF, 0x11, 0x0E,
  0x00, 0x00, 0x02, 0x01, 0x89, 0x8A, 0xBE, 0x47,
  0x00, 0x80, 0x00, 0x00, 0x00, 0x99
};

const unsigned long FAZA_NASLUCHU_MS = 20000UL;
const unsigned long ODSTEP_SONDY_MS  = 3000UL;

unsigned long startMs = 0;
unsigned long ostatniaSonda = 0;
unsigned long ostatniBajt = 0;

// prosty parser ramek
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
  gree.write(PROBE, sizeof(PROBE));   // SoftwareSerial nadaje blokujaco
  digitalWrite(PIN_DIR, LOW);         // od razu wracamy na nasluch
}

void analizujBufor() {
  // szukaj naglowka 7E 7E
  while (bufLen >= 6) {
    if (buf[0] != 0x7E || buf[1] != 0x7E) {
      memmove(buf, buf + 1, --bufLen);
      continue;
    }
    uint8_t dlBody = buf[5];
    uint8_t total  = 6 + dlBody;      // 7E 7E src dst 11 len + body(z suma)
    if (total > sizeof(buf)) {        // smiec - odrzuc naglowek
      memmove(buf, buf + 2, bufLen -= 2);
      continue;
    }
    if (bufLen < total) return;       // ramka jeszcze niekompletna

    // mamy pelna ramke
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
  digitalWrite(PIN_DIR, LOW);         // nasluch
  Serial.begin(115200);
  gree.begin(1200);
  startMs = millis();
  Serial.println(F("=== SONDA COM-MANUAL / Gree GKH ==="));
  Serial.println(F("Faza 1: 20 s czystego nasluchu..."));
}

void loop() {
  // odbior
  while (gree.available()) {
    uint8_t b = gree.read();
    if (millis() - ostatniBajt > 200) Serial.print(F("\n[RX] "));
    ostatniBajt = millis();
    hex2(b);
    if (bufLen < sizeof(buf)) buf[bufLen++] = b;
    analizujBufor();
  }

  // sondowanie po fazie nasluchu
  if (millis() - startMs > FAZA_NASLUCHU_MS &&
      millis() - ostatniaSonda > ODSTEP_SONDY_MS) {
    ostatniaSonda = millis();
    wyslijSonde();
  }
}

/* ---------------------------------------------------------------
 * WARIANT ESP32 (gdybys wolal ESP32 zamiast UNO):
 *   - zamiast SoftwareSerial uzyj Serial2: RX=GPIO16, TX=GPIO17,
 *     Serial2.begin(1200, SERIAL_8N1, 16, 17);
 *   - PIN_DIR np. GPIO4;
 *   - reszta logiki bez zmian (gree -> Serial2).
 * --------------------------------------------------------------- */
