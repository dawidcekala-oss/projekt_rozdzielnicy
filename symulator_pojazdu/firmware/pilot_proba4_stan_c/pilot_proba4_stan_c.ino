// ============================================================================
// Symulator pojazdu EV - proba 4: pelna sesja az do stanu C
// AMPERE POINT, 23 IX 2026
//
// UWAGA: TA PROBA WPROWADZA LADOWARKE W STAN LADOWANIA.
//   Stycznik ladowarki sie zamknie i na gniezdzie wyjsciowym testera pojawi
//   sie napiecie sieci. Trwa to 15 sekund, potem program sam wraca do stanu B
//   i stycznik ma sie otworzyc.
//
// PRZEBIEG ZAPISU (sekundy od chwili, gdy pojawi sie pilot)
//    0 -  4   wszystkie cewki odpuszczone     spodziewane 9,2 V i modulacja
//    5 - 19   zwarta galaz ladowania 1302 om  spodziewane 5,9 V, STYCZNIK ZAMKNIETY
//   20 - 29   galaz rozwarta                  powrot do 9,2 V, stycznik otwarty
//   30 - 34   zasilona cewka zaniku pojazdu   12,6 V, modulacja gasnie
//   35 - ...  cewka odpuszczona               powrot do 9,2 V
//   dalej     zapis leci do konca pamieci (204 s)
//
// BEZPIECZNY KIERUNEK
//   Kazdy zanik zasilania elektroniki odpuszcza wszystkie cewki. Galaz
//   ladowania sie rozwiera, pilot wraca na 9 V i ladowarka otwiera stycznik.
//   Zeby napiecie sie utrzymalo, procesor musi CIAGLE trzymac cewke.
//
// POLACZENIA
//   A1  <- wezel A' toru analogowego
//   D8  <- wyjscie komparatora (nozka 1)
//   D11 -> ULN wejscie 1 (wyjscie 16) - zwarcie pilota do masy
//   D10 -> ULN wejscie 2 (wyjscie 15) - galaz ladowania 1302 om
//   D9  -> ULN wejscie 3 (wyjscie 14) - ominiecie diody pojazdu
//   D7  -> ULN wejscie 4 (wyjscie 13) - zanik pojazdu (zasilona = pojazd znika)
//
// ZASADA
//   Albo laptop, albo wtyczka. Nigdy jedno i drugie naraz.
// ============================================================================
#include <EEPROM.h>

const uint8_t P_WEZEL   = A1;
const uint8_t P_ZWARCIE = 11;
const uint8_t P_LADOW   = 10;
const uint8_t P_DIODA   =  9;
const uint8_t P_ZANIK   =  7;

const int      EE_N    = 0;
const int      EE_VCC  = 2;
const int      EE_DAT  = 4;
const uint8_t  REK     = 5;
const uint16_t MAXREK  = (uint16_t)((1024 - EE_DAT) / REK);   // 204

const uint16_t T_C_OD     =  5;   // sekunda wejscia w stan C
const uint16_t T_C_DO     = 20;   // sekunda wyjscia ze stanu C
const uint16_t T_ZNIKA    = 30;
const uint16_t T_WRACA    = 35;

float    VCC      = 5.00;
bool     nagrywa  = false;
uint16_t nrek     = 0;
uint32_t t_nast   = 0;
float    u_odniesienia = 0;

// --- przechwytywanie sprzetowe: Timer1, wejscie ICP1 = D8 -------------------
volatile uint16_t t_prev = 0;
volatile uint32_t sumH = 0, sumL = 0;
volatile uint16_t nH = 0, nL = 0;

ISR(TIMER1_CAPT_vect) {
  uint16_t t  = ICR1;
  uint16_t dt = t - t_prev;
  t_prev = t;
  if (TCCR1B & _BV(ICES1)) { sumL += dt; nL++; }
  else                     { sumH += dt; nH++; }
  TCCR1B ^= _BV(ICES1);
}

float zmierzVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(5);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC));
  uint16_t w = ADC;
  return (w == 0) ? 5.00 : 1125.3 / w;
}

bool zmierzPWM(float &okres, float &wypelnienie) {
  noInterrupts();
  uint32_t sh = sumH, sl = sumL; uint16_t nh = nH, nl = nL;
  sumH = sumL = 0; nH = nL = 0;
  interrupts();
  if (nh < 5 || nl < 5) return false;
  float th = (float)sh / nh * 0.5;
  float tl = (float)sl / nl * 0.5;
  okres = th + tl;
  wypelnienie = 100.0 * tl / okres;      // komparator odwraca
  return true;
}

float poziomPilota() {
  uint16_t szczyt = 0;
  for (uint16_t i = 0; i < 300; i++) {
    uint16_t v = analogRead(P_WEZEL);
    if (v > szczyt) szczyt = v;
  }
  float uA = szczyt * VCC / 1023.0;
  return (uA - 0.3636 * VCC) / 0.1515;
}

const __FlashStringHelper* nazwaStanu(float uCP, bool jest_pwm) {
  if (!jest_pwm && uCP > 1.5 && uCP < 3.5) return F("pilot niepodlaczony");
  if (uCP > 10.5) return F("A brak pojazdu");
  if (uCP >  7.5) return F("B pojazd zgloszony");
  if (uCP >  4.5) return F("C LADOWANIE");
  if (uCP >  1.5) return F("D wentylacja (NIE POWINNO WYSTAPIC)");
  if (uCP > -1.5) return F("E zwarcie pilota");
  return F("nieokreslony");
}

void opiszPrzekazniki(uint8_t p) {
  if (p == 0) { Serial.print(F("spoczynek")); return; }
  bool pierwszy = true;
  if (p & 0x01) { Serial.print(F("ZANIK POJAZDU")); pierwszy = false; }
  if (p & 0x02) { if (!pierwszy) Serial.print('+'); Serial.print(F("LADOWANIE")); pierwszy = false; }
  if (p & 0x04) { if (!pierwszy) Serial.print('+'); Serial.print(F("BEZ DIODY")); pierwszy = false; }
  if (p & 0x08) { if (!pierwszy) Serial.print('+'); Serial.print(F("ZWARCIE")); }
}

// ============================================================================
void wysypZapis() {
  uint16_t n, mv;
  EEPROM.get(EE_N, n);
  EEPROM.get(EE_VCC, mv);
  Serial.println();
  Serial.println(F("============ ZAPIS Z POPRZEDNIEJ SESJI ============"));
  if (n == 0 || n == 0xFFFF) {
    Serial.println(F("brak zapisu"));
    Serial.println(F("==================================================="));
    Serial.println();
    return;
  }
  if (n > MAXREK) n = MAXREK;
  Serial.print(F("zasilanie w czasie zapisu = "));
  Serial.print(mv / 1000.0, 3); Serial.println(F(" V"));
  Serial.print(F("rekordow: ")); Serial.print(n);
  Serial.print(F("   (co 1 s, czyli ")); Serial.print(n); Serial.println(F(" s nagrania)"));
  Serial.println(F("s;pilot_V;wypelnienie_%;oferta_A;przekazniki;stan"));
  for (uint16_t i = 0; i < n; i++) {
    int16_t  u; uint16_t d; uint8_t p;
    EEPROM.get(EE_DAT + i * REK,     u);
    EEPROM.get(EE_DAT + i * REK + 2, d);
    EEPROM.get(EE_DAT + i * REK + 4, p);
    float uCP = u / 100.0;
    Serial.print(i);               Serial.print(';');
    Serial.print(uCP, 2);          Serial.print(';');
    if (d == 0xFFFF) {
      Serial.print(F("-;-;"));
    } else {
      float dd = d / 100.0;
      float I  = (dd <= 85.0) ? 0.6 * dd : 2.5 * (dd - 64.0);
      Serial.print(dd, 2);         Serial.print(';');
      Serial.print(I, 1);          Serial.print(';');
    }
    opiszPrzekazniki(p);           Serial.print(';');
    Serial.println(nazwaStanu(uCP, d != 0xFFFF));
  }
  Serial.println(F("==================================================="));
  Serial.println();
}

uint8_t stanPrzekaznikow() {
  uint8_t p = 0;
  if (digitalRead(P_ZANIK))   p |= 0x01;
  if (digitalRead(P_LADOW))   p |= 0x02;
  if (digitalRead(P_DIODA))   p |= 0x04;
  if (digitalRead(P_ZWARCIE)) p |= 0x08;
  return p;
}

void zapiszRekord(float uCP, bool jest_pwm, float duty) {
  if (nrek >= MAXREK) return;
  int16_t  u = (int16_t)(uCP * 100.0);
  uint16_t d = jest_pwm ? (uint16_t)(duty * 100.0) : 0xFFFF;
  uint8_t  p = stanPrzekaznikow();
  EEPROM.put(EE_DAT + nrek * REK,     u);
  EEPROM.put(EE_DAT + nrek * REK + 2, d);
  EEPROM.put(EE_DAT + nrek * REK + 4, p);
  nrek++;
  EEPROM.put(EE_N, nrek);
}

void sprawdzPodlaczenia() {
  pinMode(P_WEZEL, INPUT);        delay(5);
  pinMode(P_WEZEL, INPUT_PULLUP); delay(10);
  analogRead(P_WEZEL); delayMicroseconds(200);
  uint32_t s = 0;
  for (uint8_t i = 0; i < 16; i++) s += analogRead(P_WEZEL);
  float v2 = s / 16.0 * VCC / 1023.0;
  pinMode(P_WEZEL, INPUT);        delay(5);

  pinMode(8, INPUT);        delay(5);  int d1 = digitalRead(8);
  pinMode(8, INPUT_PULLUP); delay(10); int d2 = digitalRead(8);
  pinMode(8, INPUT);        delay(5);

  Serial.print(F("A1 wezel A prim  "));
  Serial.println(v2 < VCC - 0.30 ? F("podlaczone") : F("NIEPODLACZONE  <<< BLAD"));
  Serial.print(F("D8 komparator  "));
  if (d1 == 0 && d2 == 0) Serial.println(F("podlaczone, wyjscie nisko (tak ma byc)"));
  else                    Serial.println(F("wysoko albo niepodlaczone"));

  float uCP = poziomPilota();
  Serial.print(F("dioda pojazdu  pilot bez wtyczki "));
  Serial.print(uCP, 2); Serial.print(F(" V  ->  "));
  if (uCP < 1.0)      Serial.println(F("przewodzi, galaz pojazdu podpieta (tak ma byc)"));
  else if (uCP < 3.5) Serial.println(F("NIE PRZEWODZI - dioda odwrotnie?"));
  else                Serial.println(F("wtyczka chyba wpieta - odepnij ja"));
}

void werdykt(float odniesienie, float teraz, bool ma_spadac, const __FlashStringHelper* co) {
  float zmiana = teraz - odniesienie;
  Serial.print(F(">>> ")); Serial.print(co);
  Serial.print(F(": pilot ")); Serial.print(odniesienie, 2);
  Serial.print(F(" -> ")); Serial.print(teraz, 2);
  Serial.print(F(" V, zmiana ")); Serial.print(zmiana, 2); Serial.print(F(" V - "));
  bool ok = ma_spadac ? (zmiana < -1.5) : (zmiana > 1.5);
  Serial.println(ok ? F("ZGODNIE Z OCZEKIWANIEM") : F("BRAK REAKCJI"));
}

// ============================================================================
void setup() {
  pinMode(P_ZWARCIE, OUTPUT); digitalWrite(P_ZWARCIE, LOW);
  pinMode(P_LADOW,   OUTPUT); digitalWrite(P_LADOW,   LOW);
  pinMode(P_DIODA,   OUTPUT); digitalWrite(P_DIODA,   LOW);
  pinMode(P_ZANIK,   OUTPUT); digitalWrite(P_ZANIK,   LOW);

  Serial.begin(115200);
  pinMode(8, INPUT);
  TCCR1A = 0;
  TCCR1B = _BV(ICNC1) | _BV(ICES1) | _BV(CS11);
  TIMSK1 = _BV(ICIE1);
  delay(600);
  VCC = zmierzVcc();

  wysypZapis();

  Serial.println(F("===== PROBA 4: PELNA SESJA ZE STANEM C ====="));
  Serial.print(F("zasilanie = ")); Serial.print(VCC, 3); Serial.println(F(" V"));
  sprawdzPodlaczenia();
  Serial.println(F("UWAGA: w 5 s wchodze w stan C - STYCZNIK SIE ZAMKNIE"));
  Serial.println(F("       w 20 s wracam do stanu B - stycznik sie otworzy"));
  Serial.println(F("============================================"));
  Serial.println();

  t_nast = millis() + 1000;
}

void loop() {
  if ((int32_t)(millis() - t_nast) < 0) return;
  t_nast += 1000;

  float okres = 0, duty = 0;
  bool  jest_pwm = zmierzPWM(okres, duty);
  float uCP = poziomPilota();

  if (!nagrywa && (jest_pwm || uCP > 4.0)) {
    nagrywa = true;
    nrek = 0;
    EEPROM.put(EE_VCC, (uint16_t)(VCC * 1000.0));
    Serial.println(F(">>> POJAWILA SIE LADOWARKA - ZACZYNAM ZAPIS <<<"));
  }

  Serial.print(F("pilot ")); Serial.print(uCP, 2); Serial.print(F(" V | "));
  Serial.print(nazwaStanu(uCP, jest_pwm));
  if (jest_pwm) {
    float I = (duty <= 85.0) ? 0.6 * duty : 2.5 * (duty - 64.0);
    Serial.print(F(" | okres ")); Serial.print(okres, 0);
    Serial.print(F(" us | wypelnienie ")); Serial.print(duty, 2);
    Serial.print(F(" % | oferta ")); Serial.print(I, 1); Serial.print(F(" A"));
    if (duty < 3.0 || (duty > 7.0 && duty < 8.0) || duty > 97.0)
      Serial.print(F("  <<< STREFA ZABRONIONA"));
    else if (duty >= 3.0 && duty <= 7.0)
      Serial.print(F("  <<< zadanie lacza cyfrowego"));
  } else {
    Serial.print(F(" | brak modulacji"));
  }

  if (nagrywa) {
    if (nrek < MAXREK) {
      zapiszRekord(uCP, jest_pwm, duty);
      Serial.print(F("  [zapis ")); Serial.print(nrek); Serial.print('/');
      Serial.print(MAXREK); Serial.print(']');
    } else {
      Serial.print(F("  [pamiec pelna]"));
    }
  }
  Serial.println();

  if (!nagrywa) return;

  // --- harmonogram ---------------------------------------------------------
  if (nrek == T_C_OD && !digitalRead(P_LADOW)) {
    u_odniesienia = uCP;
    digitalWrite(P_LADOW, HIGH);
    Serial.println(F(">>> ZADAM LADOWANIA - stan C, stycznik ma sie zamknac <<<"));
  }
  if (nrek == T_C_OD + 2) werdykt(u_odniesienia, uCP, true, F("wejscie w stan C"));

  if (nrek == T_C_DO && digitalRead(P_LADOW)) {
    u_odniesienia = uCP;
    digitalWrite(P_LADOW, LOW);
    Serial.println(F(">>> KONCZE LADOWANIE - powrot do stanu B <<<"));
  }
  if (nrek == T_C_DO + 2) werdykt(u_odniesienia, uCP, false, F("wyjscie ze stanu C"));

  if (nrek == T_ZNIKA && !digitalRead(P_ZANIK)) {
    u_odniesienia = uCP;
    digitalWrite(P_ZANIK, HIGH);
    Serial.println(F(">>> KAZE POJAZDOWI ZNIKNAC <<<"));
  }
  if (nrek == T_ZNIKA + 2) werdykt(u_odniesienia, uCP, false, F("zanik pojazdu"));

  if (nrek == T_WRACA && digitalRead(P_ZANIK)) {
    u_odniesienia = uCP;
    digitalWrite(P_ZANIK, LOW);
    Serial.println(F(">>> POJAZD WRACA <<<"));
  }
  if (nrek == T_WRACA + 2) werdykt(u_odniesienia, uCP, true, F("powrot pojazdu"));
}
