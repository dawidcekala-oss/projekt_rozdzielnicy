// ============================================================================
// Symulator pojazdu EV - czy wejscie PP przezylo faze
// AMPERE POINT, 23 IX 2026
//
// PO CO
//   Przewod doprowadzajacy PP do procesora byl przez chwile podlaczony do fazy.
//   PP idzie na A2. Trzeba ustalic, czy nozka A2 i rezystor 1 kom do +5 V to
//   przezyly, zanim cokolwiek do tego wejscia wpiszemy w programie.
//
// JAK TO DZIALA
//   Kazda nozka przechodzi trzy proby:
//     1. z podciagnieciem wewnetrznym - zdrowa, nieobciazona nozka daje ~5 V
//     2. wysterowana w dol - zdrowa nozka schodzi ponizej 0,3 V nawet przy
//        5 mA, ktore plynie przez rezystor 1 kom; wyzszy odczyt = slaby drajwer
//     3. puszczona wolno zaraz po wysterowaniu w dol - jesli na nozce wisi
//        rezystor 1 kom do +5 V, napiecie wraca natychmiast; jesli nozka nie
//        jest nigdzie podpieta, zostaje przy zerze i pelznie do gory
//
//   Trzecia proba odroznia "rezystor 1 kom caly i podpiety" od "rezystor
//   przepalony albo przewod odpiety".
//
//   A1 i A6/A7 zostaja nietkniete - A1 to tor pilota, A6/A7 nie maja
//   wyprowadzen cyfrowych, wiec da sie je tylko odczytac.
//
// ZASADA
//   Albo laptop, albo wtyczka. Ten sprawdzian przy laptopie i BEZ wtyczki.
// ============================================================================

float VCC = 5.00;

struct Nozka { uint8_t pin; const char* opis; };

const Nozka N[5] = {
  { A0, "A0  wolne" },
  { A2, "A2  PP - kodowanie kabla" },
  { A3, "A3  prad L1 (przekladnik)" },
  { A4, "A4  SDA wyswietlacza" },
  { A5, "A5  SCL wyswietlacza" }
};

float zmierzVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(5);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC));
  uint16_t w = ADC;
  return (w == 0) ? 5.00 : 1125.3 / w;
}

float napiecie(uint8_t pin) {
  analogRead(pin); delayMicroseconds(300);
  uint32_t s = 0;
  for (uint8_t i = 0; i < 32; i++) s += analogRead(pin);
  return s / 32.0 * VCC / 1023.0;
}

void setup() {
  Serial.begin(115200);
  delay(800);
  VCC = zmierzVcc();

  Serial.println();
  Serial.println(F("======= CZY WEJSCIA PRZEZYLY FAZE ======="));
  Serial.print(F("zasilanie = ")); Serial.print(VCC, 3); Serial.println(F(" V"));
  if (VCC < 4.6 || VCC > 5.4) Serial.println(F("  <<< ZASILANIE POZA NORMA"));
  Serial.println(F("WTYCZKA MUSI BYC WYJETA"));
  Serial.println();

  // tor pilota jako punkt odniesienia - wiadomo, ze dziala
  pinMode(A1, INPUT);
  Serial.print(F("A1  tor pilota (odniesienie): "));
  Serial.print(napiecie(A1), 3); Serial.println(F(" V"));
  Serial.println();

  for (uint8_t i = 0; i < 5; i++) {
    uint8_t p = N[i].pin;

    pinMode(p, INPUT_PULLUP); delay(20);
    float v_podc = napiecie(p);

    pinMode(p, OUTPUT); digitalWrite(p, LOW); delay(20);
    float v_dol = napiecie(p);

    pinMode(p, INPUT);                       // puszczone wolno
    float v_zaraz = napiecie(p);
    delay(150);
    float v_pozniej = napiecie(p);

    pinMode(p, INPUT_PULLUP); delay(20);
    pinMode(p, INPUT);

    Serial.println(N[i].opis);
    Serial.print(F("     podciagniete ")); Serial.print(v_podc, 3);
    Serial.print(F(" V | wysterowane w dol ")); Serial.print(v_dol, 3);
    Serial.print(F(" V | puszczone ")); Serial.print(v_zaraz, 3);
    Serial.print(F(" -> ")); Serial.print(v_pozniej, 3); Serial.println(F(" V"));

    Serial.print(F("     -> "));
    if (v_dol > 0.35) {
      Serial.println(F("NOZKA USZKODZONA - nie sciaga do zera"));
    } else if (v_podc < VCC - 0.60) {
      Serial.print(F("cos sciaga te nozke w dol nawet przy podciagnieciu ("));
      Serial.print(v_podc, 2); Serial.println(F(" V) - sprawdzic"));
    } else if (v_zaraz > VCC * 0.8) {
      Serial.println(F("nozka sprawna, wisi na niej mocne podciagniecie (rezystor 1 kom)"));
    } else if (v_pozniej > v_zaraz + 0.3) {
      Serial.println(F("nozka sprawna, nic do niej nie podpiete"));
    } else {
      Serial.println(F("nozka sprawna, wejscie zostaje przy zerze - cos ja trzyma nisko"));
    }
    Serial.println();
  }

  Serial.println(F("--- czego sie spodziewam na A2 ---"));
  Serial.println(F("Rezystor 1 kom do +5 V caly i podpiety, wtyczka wyjeta:"));
  Serial.println(F("  podciagniete ~5 V, w dol ~0,03 V, puszczone ~5 V od razu."));
  Serial.println(F("Rezystor przepalony albo przewod odpiety:"));
  Serial.println(F("  puszczone zostaje przy zerze i powoli pelznie do gory."));
  Serial.println(F("========================================="));
}

void loop() { }
