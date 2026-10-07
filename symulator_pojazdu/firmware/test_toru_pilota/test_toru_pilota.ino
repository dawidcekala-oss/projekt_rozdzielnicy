// ============================================================================
// Symulator pojazdu EV - test toru pilota i podglad na zywo
// AMPERE POINT, 21 IX 2026
//
// POLACZENIA STALE
//   D8  <- wyjscie komparatora (nozka 1)
//   A1  <- wezel A' toru analogowego
//
// POLACZENIE TYLKO NA CZAS SAMOTESTU (jeden przewod, potem zdjac)
//   D5  -> 1 kohm -> wezel miedzy dwoma 100 kohm (= nozka 2 komparatora)
//   (A0 i A2 nie sa juz potrzebne - D8 dowodzi komparatora lepiej)
//
// Samotest wykonuje sie raz przy starcie, przy ODPIETEJ ladowarce.
// Potem leci podglad na zywo, raz na sekunde.
// ============================================================================

const uint8_t P_WYMUS = 5;   // TYMCZASOWO: w projekcie D5 to przycisk start/stop
const uint8_t P_PROG  = A0;
const uint8_t P_WYJ   = A2;
const uint8_t P_WEZEL = A1;

float VCC = 5.00;              // ustalane automatycznie w setup()
bool a0_jest = false, a2_jest = false;   // czy przewody pomocnicze sa wpiete

// --- przechwytywanie sprzetowe: Timer1, wejscie ICP1 = D8 --------------------
volatile uint16_t t_prev = 0;
volatile uint32_t sumH = 0, sumL = 0;
volatile uint16_t nH = 0, nL = 0;

ISR(TIMER1_CAPT_vect) {
  uint16_t t  = ICR1;
  uint16_t dt = t - t_prev;          // arytmetyka 16-bit zawija sie sama
  t_prev = t;
  if (TCCR1B & _BV(ICES1)) { sumL += dt; nL++; }   // zlapane zbocze narastajace
  else                     { sumH += dt; nH++; }
  TCCR1B ^= _BV(ICES1);              // nastepnym razem przeciwne zbocze
}

// --- pomiar wlasnego napiecia zasilania wzgledem zrodla odniesienia 1,1 V ----
float zmierzVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(5);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC));
  uint16_t w = ADC;
  if (w == 0) return 5.00;
  return 1125.3 / w;                 // 1,1 * 1023 / odczyt  [V]
}

float volt(uint8_t p) {
  analogRead(p); delayMicroseconds(200);
  uint32_t s = 0;
  for (uint8_t i = 0; i < 16; i++) s += analogRead(p);
  return s / 16.0 * VCC / 1023.0;
}

void ocen(const __FlashStringHelper* co, float v, float lo, float hi) {
  Serial.print(co);
  Serial.print(F(" = ")); Serial.print(v, 3); Serial.print(F(" V"));
  Serial.print(F("   oczek. ")); Serial.print(lo, 2);
  Serial.print(F("..")); Serial.print(hi, 2);
  Serial.println((v >= lo && v <= hi) ? F("   OK") : F("   <<< BLAD"));
}

bool zmierzPWM(float &okres, float &wypelnienie) {
  noInterrupts();
  uint32_t sh = sumH, sl = sumL; uint16_t nh = nH, nl = nL;
  sumH = sumL = 0; nH = nL = 0;
  interrupts();
  if (nh < 5 || nl < 5) return false;
  float th = (float)sh / nh * 0.5;          // us
  float tl = (float)sl / nl * 0.5;          // us
  okres = th + tl;
  wypelnienie = 100.0 * tl / okres;         // komparator odwraca:
  return true;                              // dol na D8 = gora pilota
}

// --- czy wejscia sa w ogole do czegos podlaczone -----------------------------
// Wlaczenie wewnetrznego podciagniecia (ok. 40 kohm do 5 V): pin wiszacy
// w powietrzu skacze na pelne zasilanie, pin podlaczony do dzielnika zostaje
// znacznie nizej, bo dzielnik ma male rezystancje zastepcze.
void sprawdzPodlaczenia() {
  Serial.println(F("--- kontrola podlaczen ---"));
  const uint8_t piny[3] = { P_PROG, P_WEZEL, P_WYJ };
  for (uint8_t i = 0; i < 3; i++) {
    pinMode(piny[i], INPUT);        delay(5);  float v1 = volt(piny[i]);
    pinMode(piny[i], INPUT_PULLUP); delay(10); float v2 = volt(piny[i]);
    pinMode(piny[i], INPUT);        delay(5);
    if      (i == 0) Serial.print(F("A0 nozka 3 (prog)    "));
    else if (i == 1) Serial.print(F("A1 wezel A'          "));
    else             Serial.print(F("A2 nozka 1 (wyjscie) "));
    Serial.print(F("swobodnie ")); Serial.print(v1, 3);
    Serial.print(F(" V | z podciagnieciem ")); Serial.print(v2, 3);
    bool jest = (v2 < VCC - 0.30);
    if (i == 0) a0_jest = jest;
    if (i == 2) a2_jest = jest;
    Serial.println(jest ? F(" V  -> podlaczone") : F(" V  -> WISI W POWIETRZU"));
  }
  pinMode(8, INPUT);        delay(5);  int d1 = digitalRead(8);
  pinMode(8, INPUT_PULLUP); delay(10); int d2 = digitalRead(8);
  pinMode(8, INPUT);        delay(5);
  Serial.print(F("D8 wyjscie komparatora  swobodnie "));
  Serial.print(d1 ? F("WYSOKO") : F("NISKO"));
  Serial.print(F(" | z podciagnieciem "));
  Serial.print(d2 ? F("WYSOKO") : F("NISKO"));
  if (d1 == 0 && d2 == 0) Serial.println(F("  -> podlaczone, wyjscie nisko (tak ma byc)"));
  else                    Serial.println(F("  -> wysoko albo WISI W POWIETRZU"));
  Serial.println();
}

// ============================================================================
void samotest() {
  Serial.println();
  Serial.println(F("================ SAMOTEST TORU PILOTA ================"));
  Serial.print(F("napiecie zasilania (zmierzone samodzielnie) = "));
  Serial.print(VCC, 3); Serial.println(F(" V"));
  Serial.println(F("ladowarka ma byc ODPIETA"));
  Serial.println();

  sprawdzPodlaczenia();

  // --- przelaczanie komparatora, oceniane WYLACZNIE przez D8 ---------------
  pinMode(8, INPUT);
  pinMode(P_WYMUS, OUTPUT);
  digitalWrite(P_WYMUS, HIGH); delay(10);
  int d_gora = digitalRead(8);          // wezel wysoko -> wyjscie ma byc NISKO
  float prog_a = volt(P_PROG), wyj_a = volt(P_WYJ);
  digitalWrite(P_WYMUS, LOW);  delay(10);
  int d_dol  = digitalRead(8);          // wezel nisko  -> wyjscie ma byc WYSOKO
  float prog_b = volt(P_PROG), wyj_b = volt(P_WYJ);

  Serial.print(F("wezel wysoko -> D8 "));
  Serial.print(d_gora ? F("WYSOKO") : F("NISKO"));
  Serial.print(F("   |   wezel nisko -> D8 "));
  Serial.println(d_dol ? F("WYSOKO") : F("NISKO"));

  if (d_gora == 0 && d_dol == 1) {
    Serial.println(F("KOMPARATOR PRZELACZA W OBIE STRONY   OK"));
  } else if (d_gora == d_dol) {
    Serial.println(F("brak reakcji  <<< brak przewodu D5 -> 1 kohm -> wezel dzielnika,"));
    Serial.println(F("               albo przewod trafil w zly punkt"));
  } else {
    Serial.println(F("reakcja ODWROTNA  <<< zamienione wejscia 2 i 3 komparatora"));
  }

  // wartosci pomocnicze - tylko gdy ktos wpial A0 / A2, inaczej to smieci
  if (a0_jest) {
    ocen(F("prog przy wyjsciu niskim   "), prog_a, 0.40, 0.49);
    ocen(F("prog przy wyjsciu wysokim  "), prog_b, 0.50, 0.58);
    ocen(F("HISTEREZA (roznica progow) "), prog_b - prog_a, 0.07, 0.12);
  }
  if (a2_jest) {
    ocen(F("wyjscie, wezel wysoko      "), wyj_a, 0.00, 0.50);
    ocen(F("wyjscie, wezel nisko       "), wyj_b, 4.30, 5.20);
  }

  Serial.println();
  if (d_gora == d_dol) {
    // brak przewodu testowego - nie ma czym wymusic przelaczania, wiec
    // pomiar wypelnienia na sucho nie ma sensu. To nie jest blad.
    Serial.println(F("pomiar wypelnienia na sucho POMINIETY"));
    Serial.println(F("(wymaga przewodu D5 -> 1 kohm -> wezel dzielnika; zweryfikuje go pilot)"));
    pinMode(P_WYMUS, INPUT);
    delay(20);
    Serial.println();
    float wa0 = volt(P_WEZEL);
    Serial.print(F("wezel pomiarowy przy odpietym pilocie = "));
    Serial.print(wa0, 3);
    if (wa0 > VCC - 0.30) Serial.println(F(" V   <<< A1 nie podlaczone"));
    else Serial.println(F(" V   (oczek. 2,14)"));
    Serial.println(F("======================================================"));
    Serial.println();
    return;
  }
  analogWrite(P_WYMUS, 136);                 // 136/255 = 53,33 %
  delay(300);
  noInterrupts(); sumH = sumL = 0; nH = nL = 0; interrupts();
  delay(600);
  float okres, d;
  if (zmierzPWM(okres, d)) {
    Serial.print(F("okres         = ")); Serial.print(okres, 1);
    Serial.println(F(" us   (oczek. ok. 1024)"));
    Serial.print(F("wypelnienie   = ")); Serial.print(d, 2);
    Serial.print(F(" %    oczek. 53,33"));
    Serial.println(fabs(d - 53.33) < 1.5 ? F("   OK") : F("   <<< BLAD"));
    Serial.print(F("prad z tabeli = ")); Serial.print(0.6 * d, 1);
    Serial.println(F(" A    (oczek. 32,0)"));
  } else {
    Serial.println(F("licznik nie widzi zbocz na D8   <<< BLAD"));
    Serial.println(F("sprawdz przewod D8 i rezystor podciagajacy 10 kohm"));
  }

  pinMode(P_WYMUS, INPUT);                   // zwolnij nozke 2
  delay(20);
  Serial.println();
  float wa = volt(P_WEZEL);
  Serial.print(F("wezel pomiarowy przy odpietym pilocie = "));
  Serial.print(wa, 3);
  if (wa > VCC - 0.30) Serial.println(F(" V   <<< A1 nie podlaczone"));
  else Serial.println(F(" V   (oczek. 2,14)"));
  Serial.println(F("======================================================"));
  Serial.println(F("ZDEJMIJ przewod testowy. Zaczynam podglad."));
  Serial.println();
}

// ============================================================================
void setup() {
  Serial.begin(115200);
  pinMode(8, INPUT);
  TCCR1A = 0;
  TCCR1B = _BV(ICNC1) | _BV(ICES1) | _BV(CS11);   // filtr, zbocze nar., /8
  TIMSK1 = _BV(ICIE1);
  delay(600);
  VCC = zmierzVcc();
  samotest();
}

void loop() {
  delay(1000);

  uint16_t szczyt = 0;                       // szczyt dodatni = max z 300 probek
  for (uint16_t i = 0; i < 300; i++) {
    uint16_t v = analogRead(P_WEZEL);
    if (v > szczyt) szczyt = v;
  }
  float uA  = szczyt * VCC / 1023.0;
  float uCP = (uA - 0.3636 * VCC) / 0.1515;

  float okres, d;
  bool jest_pwm = zmierzPWM(okres, d);

  // Bez modulacji i z poziomem w okolicy wartosci jalowej (2,4 V) pilot
  // po prostu nie jest podlaczony - to nie jest zaden stan pojazdu.
  bool pilot_odpiety = (!jest_pwm && uCP > 1.5 && uCP < 3.5);

  const __FlashStringHelper* stan;
  if      (pilot_odpiety) stan = F("pilot NIEPODLACZONY");
  else if (uCP > 10.5) stan = F("A brak polaczenia  ");
  else if (uCP >  7.5) stan = F("B podlaczony       ");
  else if (uCP >  4.5) stan = F("C LADOWANIE        ");
  else if (uCP >  1.5) stan = F("D wentylacja !!    ");
  else if (uCP > -1.5) stan = F("E zwarcie pilota   ");
  else                 stan = F("? nieokreslony     ");

  Serial.print(F("pilot ")); Serial.print(uCP, 2);
  Serial.print(F(" V | ")); Serial.print(stan);

  if (jest_pwm) {
    float I = (d <= 85.0) ? 0.6 * d : 2.5 * (d - 64.0);
    Serial.print(F(" | okres ")); Serial.print(okres, 0);
    Serial.print(F(" us | wypelnienie ")); Serial.print(d, 2);
    Serial.print(F(" % | oferta ")); Serial.print(I, 1); Serial.print(F(" A"));
    if (d < 3.0 || (d > 7.0 && d < 8.0) || d > 97.0)
      Serial.print(F("  <<< STREFA ZABRONIONA"));
    else if (d >= 3.0 && d <= 7.0)
      Serial.print(F("  <<< zadanie lacza cyfrowego"));
  } else {
    Serial.print(F(" | brak modulacji"));
  }
  Serial.println();
}
