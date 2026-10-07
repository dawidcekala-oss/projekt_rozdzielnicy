// ============================================================================
// Symulator pojazdu EV - sprawdzian przekaznikow
// AMPERE POINT, 23 IX 2026
//
// PO CO
//   W probie 2 program zalaczyl przekaznik obecnosci pojazdu, a pilot
//   ladowarki nie drgnal. Trzeba ustalic, czy przekazniki w ogole cokolwiek
//   robia z linia pilota i ktory z nich co robi.
//
// JAK TO DZIALA
//   Wtyczka MUSI byc wyjeta. Wtedy wejscie pilota nie jest nigdzie podparte
//   i stoi na wlasnym poziomie spoczynkowym okolo 2,4 V. Kazda galaz, ktora
//   przekaznik dolaczy miedzy pilota a mase, sciaga ten poziom do zera -
//   uklad mierzy to sam, bez miernika.
//
//   Program po kolei zalacza kazdy z czterech przekaznikow, nigdy dwa naraz,
//   i porownuje poziom przed i w trakcie.
//
// ZASADA
//   Albo laptop, albo wtyczka. Ten sprawdzian jest przy laptopie i BEZ wtyczki.
// ============================================================================

const uint8_t P_WEZEL = A1;

struct Przekaznik { uint8_t pin; const char* nazwa; };

const Przekaznik PRZ[4] = {
  { 11, "zwarcie pilota do masy   (ULN wejscie 1, wyjscie 16)" },
  { 10, "galaz ladowania 1302 om  (ULN wejscie 2, wyjscie 15)" },
  {  9, "ominiecie diody pojazdu  (ULN wejscie 3, wyjscie 14)" },
  {  7, "obecnosc pojazdu 2742 om (ULN wejscie 4, wyjscie 13)" }
};

float VCC = 5.00;

float zmierzVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(5);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC));
  uint16_t w = ADC;
  return (w == 0) ? 5.00 : 1125.3 / w;
}

// srednia z 200 probek - bez ladowarki nie ma przebiegu, wiec szczyt niepotrzebny
float poziomWezla() {
  uint32_t s = 0;
  for (uint16_t i = 0; i < 200; i++) s += analogRead(P_WEZEL);
  return s / 200.0 * VCC / 1023.0;
}

float naPilota(float uA) { return (uA - 0.3636 * VCC) / 0.1515; }

void wszystkieWSpoczynek() {
  for (uint8_t i = 0; i < 4; i++) digitalWrite(PRZ[i].pin, LOW);
  delay(150);
}

void setup() {
  for (uint8_t i = 0; i < 4; i++) { pinMode(PRZ[i].pin, OUTPUT); digitalWrite(PRZ[i].pin, LOW); }
  Serial.begin(115200);
  delay(800);
  VCC = zmierzVcc();

  Serial.println();
  Serial.println(F("========= SPRAWDZIAN PRZEKAZNIKOW ========="));
  Serial.print(F("zasilanie = ")); Serial.print(VCC, 3); Serial.println(F(" V"));
  Serial.println(F("WTYCZKA MUSI BYC WYJETA"));
  Serial.println(F("==========================================="));
  Serial.println();
}

void loop() {
  wszystkieWSpoczynek();
  float uA0 = poziomWezla();
  Serial.print(F("spoczynek: wezel ")); Serial.print(uA0, 3);
  Serial.print(F(" V  ->  pilot ")); Serial.print(naPilota(uA0), 2);
  Serial.println(F(" V"));

  if (naPilota(uA0) < 1.0) {
    Serial.println(F("  UWAGA: pilot juz teraz siedzi przy zerze."));
    Serial.println(F("  Albo wtyczka nadal tkwi w gniezdzie, albo cos"));
    Serial.println(F("  na stale laczy pilota z masa. Sprawdzian nic nie pokaze."));
  }
  Serial.println();

  for (uint8_t i = 0; i < 4; i++) {
    wszystkieWSpoczynek();
    float przed = poziomWezla();

    digitalWrite(PRZ[i].pin, HIGH);
    delay(300);                      // przekaznik ma czas zadzialac
    float wtrakcie = poziomWezla();
    digitalWrite(PRZ[i].pin, LOW);
    delay(300);
    float po = poziomWezla();

    float dP = naPilota(przed), dW = naPilota(wtrakcie), dO = naPilota(po);

    Serial.print(F("D")); Serial.print(PRZ[i].pin); Serial.print(F("  "));
    Serial.println(PRZ[i].nazwa);
    Serial.print(F("      pilot przed ")); Serial.print(dP, 2);
    Serial.print(F(" V | zasilona cewka ")); Serial.print(dW, 2);
    Serial.print(F(" V | po ")); Serial.print(dO, 2);
    Serial.print(F(" V | zmiana ")); Serial.print(dW - dP, 2); Serial.println(F(" V"));

    Serial.print(F("      -> "));
    if (fabs(dW - dP) > 0.8) {
      if (!(fabs(dO - dP) < 0.4))
        Serial.println(F("ZMIENIA linie pilota, ale NIE WRACA po odpuszczeniu"));
      else
        Serial.println(F("ZMIENIA linie pilota i wraca - dziala"));
    } else {
      Serial.println(F("nie rusza linii pilota"));
    }
    Serial.println();
  }

  Serial.println(F("--- runda skonczona, powtarzam za 3 s ---"));
  Serial.println();
  delay(3000);
}
