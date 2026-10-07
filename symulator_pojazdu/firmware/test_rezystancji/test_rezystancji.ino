// ============================================================================
// Symulator pojazdu EV - ile omow dokladaja przekazniki
// AMPERE POINT, 23 IX 2026
//
// PO CO
//   Poprzedni sprawdzian pokazal, ze przekaznik ominiecia diody otwiera droge
//   do masy, a przekaznik obecnosci pojazdu nie robi nic. Samo napiecie tego
//   nie rozstrzyga, bo ponizej mniej wiecej 50 kom wszystko wyglada tak samo.
//
//   Ten program kalibruje sie na dwoch znanych punktach:
//     - spoczynek            = nieskonczonosc (nic nie wisi na pilocie)
//     - zwarcie pilota (D11) = zero omow
//   i z nich wylicza, ile omow dokladaja pozostale kombinacje.
//
//   Rozdzielczosc jest na granicy mozliwosci przetwornika, wiec liczy sie
//   przede wszystkim odpowiedz: zero omow czy kilka kiloomow.
//
// ZASADA
//   Albo laptop, albo wtyczka. Sprawdzian przy laptopie i BEZ wtyczki.
// ============================================================================

const uint8_t P_WEZEL   = A1;
const uint8_t P_ZWARCIE = 11;
const uint8_t P_LADOW   = 10;
const uint8_t P_DIODA   =  9;
const uint8_t P_POJAZD  =  7;

const uint8_t  RUNDY   = 3;
const uint16_t PROBKI  = 8000;
const float    R_WEJ   = 240000.0;   // rezystor miedzy pilotem a wezlem

float VCC = 5.00;

float zmierzVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(5);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC));
  uint16_t w = ADC;
  return (w == 0) ? 5.00 : 1125.3 / w;
}

float sredniaZliczen() {
  uint32_t s = 0;
  for (uint16_t i = 0; i < PROBKI; i++) s += analogRead(P_WEZEL);
  return (float)s / PROBKI;
}

void ustaw(bool zw, bool lad, bool dio, bool poj) {
  digitalWrite(P_ZWARCIE, zw  ? HIGH : LOW);
  digitalWrite(P_LADOW,   lad ? HIGH : LOW);
  digitalWrite(P_DIODA,   dio ? HIGH : LOW);
  digitalWrite(P_POJAZD,  poj ? HIGH : LOW);
  delay(400);
}

void setup() {
  pinMode(P_ZWARCIE, OUTPUT); pinMode(P_LADOW,  OUTPUT);
  pinMode(P_DIODA,   OUTPUT); pinMode(P_POJAZD, OUTPUT);
  ustaw(false, false, false, false);

  Serial.begin(115200);
  delay(800);
  VCC = zmierzVcc();

  Serial.println();
  Serial.println(F("===== ILE OMOW DOKLADAJA PRZEKAZNIKI ====="));
  Serial.print(F("zasilanie = ")); Serial.print(VCC, 3); Serial.println(F(" V"));
  Serial.println(F("WTYCZKA MUSI BYC WYJETA"));
  Serial.println(F("=========================================="));

  for (uint8_t r = 1; r <= RUNDY; r++) {
    Serial.println();
    Serial.print(F("--- runda ")); Serial.print(r); Serial.println(F(" ---"));

    ustaw(false, false, false, false);  float c_inf = sredniaZliczen();
    ustaw(true,  false, false, false);  float c_zer = sredniaZliczen();
    ustaw(false, false, false, false);

    float V_inf = c_inf * VCC / 1023.0;
    float V_zer = c_zer * VCC / 1023.0;

    Serial.print(F("spoczynek (nic na pilocie): zliczenia "));
    Serial.print(c_inf, 2); Serial.print(F("  wezel ")); Serial.print(V_inf, 4); Serial.println(F(" V"));
    Serial.print(F("zwarcie pilota D11 (0 om):  zliczenia "));
    Serial.print(c_zer, 2); Serial.print(F("  wezel ")); Serial.print(V_zer, 4); Serial.println(F(" V"));

    if (V_inf - V_zer < 0.05) {
      Serial.println(F("!!! zwarcie pilota nic nie zmienia - kalibracja niemozliwa"));
      continue;
    }

    // kalibracja dwupunktowa
    float B = V_zer * (1.0 / R_WEJ) / (V_inf - V_zer);
    float A = V_inf * B;
    Serial.print(F("kalibracja: A = ")); Serial.print(A * 1e6, 3);
    Serial.print(F(" uA   B = ")); Serial.print(B * 1e6, 3); Serial.println(F(" uS"));
    Serial.println();

    const char* opis[4] = {
      "ominiecie diody D9",
      "ominiecie diody D9 + obecnosc pojazdu D7",
      "ominiecie diody D9 + galaz ladowania D10",
      "obecnosc pojazdu D7 sam"
    };
    bool dio[4] = { true, true,  true,  false };
    bool poj[4] = { false, true, false, true  };
    bool lad[4] = { false, false, true, false };

    for (uint8_t i = 0; i < 4; i++) {
      ustaw(false, lad[i], dio[i], poj[i]);
      float c = sredniaZliczen();
      ustaw(false, false, false, false);
      float V = c * VCC / 1023.0;

      Serial.print(opis[i]);
      Serial.print(F("\n     zliczenia ")); Serial.print(c, 2);
      Serial.print(F("  wezel ")); Serial.print(V, 4); Serial.print(F(" V  ->  "));

      float g = A / V - B;                 // przewodnosc galezi z rezystorem wejsciowym
      if (g <= 0) { Serial.println(F("brak drogi do masy")); continue; }
      float R = 1.0 / g - R_WEJ;
      if (R > 100000.0)     Serial.println(F("brak drogi do masy"));
      else if (R < -500.0)  Serial.println(F("ponizej zera - poza rozdzielczoscia"));
      else if (R < 300.0)   Serial.println(F("praktycznie zwarcie do masy"));
      else { Serial.print(F("okolo ")); Serial.print(R, 0); Serial.println(F(" om do masy")); }
    }
  }

  ustaw(false, false, false, false);
  Serial.println();
  Serial.println(F("=== koniec, przekazniki odpuszczone, juz nie pstryka ==="));
}

void loop() { }
