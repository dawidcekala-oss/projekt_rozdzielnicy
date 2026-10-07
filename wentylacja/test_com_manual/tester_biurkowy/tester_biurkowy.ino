/*
 * TESTER BIURKOWY BRAMKI (Test B) - WeMos D1 R1
 * =============================================
 * Cel: sprawdzic przy biurku, czy bramka SMG-01 (ZTS47):
 *  1) NADAJE: zamienia stan linii RXD (od WeMos D6) na roznice napiec
 *     na blaszkach A/B - mierzalne miernikiem,
 *  2) ODBIERA: zamienia wymuszony stan blaszek A/B na poziom logiczny
 *     na TXD -> dzielnik -> D5 (raportowany co sekunde po USB).
 *
 * Polaczenia jak w sondzie v2 (bez zmian):
 *   D6 (GPIO12) -> CN2 RXD,  CN2 TXD -> dzielnik 3,3k/6,5k -> D5 (GPIO14),
 *   5V -> CN2 +5V, GND wspolne. Pigtail JST NIE podlaczony do niczego.
 *
 * Tryby (komendy z portu szeregowego, 115200):
 *   'n' - NADAWANIE: D6 zmienia stan co 1 s (fala prostokatna 0,5 Hz)
 *   'o' - ODBIOR: D6 trzymany HIGH (linia w spoczynku, nadajnik zwolniony)
 *   '1' - pin D7 (kierunek, na TXP/RXP bramki) = HIGH
 *   '0' - pin D7 = LOW
 * Zawsze: raport co 1 s: stan D5 + licznik zmian + stan D7.
 */

const uint8_t PIN_RX  = 14;   // D5  <- TXD bramki (przez dzielnik)
const uint8_t PIN_TX  = 12;   // D6  -> RXD bramki
const uint8_t PIN_DIR = 13;   // D7  (nieuzywane)

bool trybNadawania = true;
bool stanTX = true;
bool stanDIR = true;
int  poprzedniD5 = -1;
unsigned long zmianyD5 = 0;
unsigned long ostatniToggle = 0, ostatniRaport = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TX, OUTPUT);
  digitalWrite(PIN_TX, HIGH);      // spoczynek UART
  pinMode(PIN_RX, INPUT);
  pinMode(PIN_DIR, OUTPUT);
  digitalWrite(PIN_DIR, HIGH);
  delay(300);
  Serial.println();
  Serial.println(F("=== TESTER BIURKOWY BRAMKI v2 (kierunek na D7) ==="));
  Serial.println(F("tryb startowy: NADAWANIE, D7=HIGH"));
  Serial.println(F("komendy: n = nadawanie, o = odbior, 1/0 = D7 HIGH/LOW"));
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'n' || c == 'N') {
      trybNadawania = true;
      Serial.println(F("[TRYB] NADAWANIE - mierz roznice A-B na blaszkach"));
    } else if (c == 'o' || c == 'O') {
      trybNadawania = false;
      digitalWrite(PIN_TX, HIGH);
      Serial.println(F("[TRYB] ODBIOR - wymuszaj stany na blaszkach A/B"));
    } else if (c == '1') {
      stanDIR = true;
      digitalWrite(PIN_DIR, HIGH);
      Serial.println(F("[DIR] D7 = HIGH"));
    } else if (c == '0') {
      stanDIR = false;
      digitalWrite(PIN_DIR, LOW);
      Serial.println(F("[DIR] D7 = LOW"));
    }
  }

  if (trybNadawania && millis() - ostatniToggle > 1000) {
    ostatniToggle = millis();
    stanTX = !stanTX;
    digitalWrite(PIN_TX, stanTX ? HIGH : LOW);
    Serial.print(F("[TX] D6 = "));
    Serial.println(stanTX ? F("HIGH (spoczynek)") : F("LOW (nadawanie 0)"));
  }

  int d = digitalRead(PIN_RX);
  if (poprzedniD5 >= 0 && d != poprzedniD5) zmianyD5++;
  poprzedniD5 = d;

  if (millis() - ostatniRaport > 1000) {
    ostatniRaport = millis();
    Serial.print(F("D5="));
    Serial.print(d);
    Serial.print(F("  zmian="));
    Serial.print(zmianyD5);
    Serial.print(trybNadawania ? F("  [nadawanie]") : F("  [odbior]"));
    Serial.println(stanDIR ? F("  D7=H") : F("  D7=L"));
  }
}
