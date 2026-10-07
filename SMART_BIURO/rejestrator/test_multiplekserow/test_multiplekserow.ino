// Program testowy nr 1 - etap 7 planu budowy rejestratora (PLAN_BUDOWY_v1)
// Co robi: co ok. 1 s przelacza adresy 0-7 obu multiplekserow CD4051BE
// i wypisuje tabelke odczytow w Monitorze portu szeregowego (115200 bodow).
// Odczyty w krokach przetwornika: 0..1023 = 0..5 V (1 krok ~ 5 mV).
//
// Polaczenia (zgodnie ze schematem PELNY):
//   D4 -> nozka 11 (A) obu CD4051BE
//   D5 -> nozka 10 (B) obu CD4051BE
//   D6 -> nozka 9  (C) obu CD4051BE
//   A2 <- nozka 3 MUX1, A3 <- nozka 3 MUX2
//   A0 <- tor CT, A1 <- tor CP, A4 <- tor 1.65 (moga byc jeszcze niepodlaczone)

const int ADR_A = 4;   // D4
const int ADR_B = 5;   // D5
const int ADR_C = 6;   // D6

void setup() {
  Serial.begin(115200);
  pinMode(ADR_A, OUTPUT);
  pinMode(ADR_B, OUTPUT);
  pinMode(ADR_C, OUTPUT);
  Serial.println();
  Serial.println(F("=== TEST MULTIPLEKSEROW REJESTRATORA ==="));
  Serial.println(F("kolumny: adres | MUX1(A2) | MUX2(A3)  [kroki 0-1023; 512 = ~2,5 V]"));
}

// jeden odczyt z odrzuceniem pierwszej probki
// (po przelaczeniu kanalu pierwsza probka niesie slad poprzedniego kanalu)
int czytaj(int pin) {
  analogRead(pin);        // probka odrzucana
  delay(2);
  return analogRead(pin); // probka wlasciwa
}

void loop() {
  Serial.println(F("---------------------------------------"));
  for (int adres = 0; adres < 8; adres++) {
    digitalWrite(ADR_A, (adres & 1) ? HIGH : LOW);
    digitalWrite(ADR_B, (adres & 2) ? HIGH : LOW);
    digitalWrite(ADR_C, (adres & 4) ? HIGH : LOW);
    delay(2);  // czas na ustalenie napiecia po zmianie adresu

    int m1 = czytaj(A2);
    int m2 = czytaj(A3);

    Serial.print(F("adres "));
    Serial.print(adres);
    Serial.print(F(" | MUX1: "));
    Serial.print(m1);
    Serial.print(F(" ("));
    Serial.print(m1 * 5.0 / 1023.0, 2);
    Serial.print(F(" V) | MUX2: "));
    Serial.print(m2);
    Serial.print(F(" ("));
    Serial.print(m2 * 5.0 / 1023.0, 2);
    Serial.println(F(" V)"));
  }

  // wejscia szybkie - odczyt niezalezny od adresu
  int ct  = czytaj(A0);
  int cp  = czytaj(A1);
  int odn = czytaj(A4);
  Serial.print(F("A0 (CT): "));
  Serial.print(ct);
  Serial.print(F(" | A1 (CP): "));
  Serial.print(cp);
  Serial.print(F(" | A4 (1.65): "));
  Serial.println(odn);

  delay(1000);
}
