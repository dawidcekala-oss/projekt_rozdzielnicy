# 02. Dobór obudowy (checkpoint 1)

Status: PROPOZYCJA do zatwierdzenia. Liczby o dostępności i cenach z Allegro są z
wyszukiwarki (strony Allegro są z tej sesji zablokowane, nie mogłem wejść w oferty).

## 1. Co musi się zmieścić (szacunek zajętości)

### 1.1 Aparatura na szynie TH35 (moduły po 18 mm)

| Grupa | Elementy | Moduły |
|-------|----------|-------:|
| Zasilanie i ochrona | rozłącznik główny 4P 63 A (4), RCD "strażnik" 4P 63 A 300 mA typ S (4), SPD T2 (4, opcja), RCD "instalacyjny" 4P 40 A 30 mA typ A (4), MCB 3P C32 odpływ 3-faz. (3), MCB 1P B16 odpływ 1-faz. (1), MCB 1P B6 ×3: sterowanie, transformator T1, zasilacz/Shelly (3) | **23** |
| Styczniki modułowe usterek | K_N 2P40 (2), K_PE 2P40 (2), K_NPEa+b 2×2P40 (4), K_L3 2P40 (2), K_INT 2P40 (2), K_R 2P40 (2), K_Tbyp/boost/buck 3×2P40 (6), K_LNa+b 2×2P25 (2), K_RCDin+byp 2×4P40 (6, opcja F13) | **28** |
| Przekaźniki 16 A (1 mod.) | K_PEr, K_PEu, K_B, K_LK | **4** |
| Shelly (szacunek, do weryfikacji po liście posiadanych) | wyjścia: 4× Shelly Pro 4PM lub mieszanka Pro 3 / Pro 1PM; pomiar: 1× Pro 3EM | **~22** |
| Zasilacz 24 V / 5 V DIN, przekaźnik kolejności faz (feedback) | | **6** |
| Rezerwa: smart licznik | np. licznik 3-faz. RS485 (4–7 mod.) | **7** |
| **Razem aparatura** | | **~90 modułów** |

Do tego listwy zaciskowe (wejście 5× 10 mm², wyjście 3-faz. 5× 6 mm², wyjście 1-faz. 3×,
licznik/DLB, sterowanie 24 V i sygnały): ok. **350–400 mm szyny**, czyli równowartość
dalszych ~20 modułów.

**Łącznie: ok. 110 modułów = 4 rzędy po 27 modułów (szyna 500 mm) lub 3 rzędy po 38 (szyna 700 mm).**

### 1.2 Elementy poza szyną (na płycie montażowej)

| Element | Gabaryt | Uwagi |
|---------|---------|-------|
| Para styczników nawrotnych 3P 32 A z blokadą (F9, zarazem stycznik główny) | ~100 × 100 × 90 mm | montaż na TH35 lub śrubami |
| Transformator toroidalny T1 400–800 VA (F10) | Ø 120–150 mm, h 55–70 mm, 3–6 kg | płasko na płycie, śruba centralna; miejsce na drugi/trzeci, jeśli kiedyś wszystkie fazy |
| Rezystor mocy 0,5 Ω / 300 W + radiator + wentylator 92 mm (F12) | ~150 × 100 × 80 mm | strefa gorąca, przy kratce wentylacyjnej |
| Rezystory 100 Ω/50 W, 6,8 kΩ/10 W, 220 kΩ | małe | na płycie obok przekaźników |
| Router / switch Wi-Fi (jeśli nie AP na ESP32) | ~120 × 80 × 30 mm | opcja |
| Przekładniki DLB na przewodach zasilających | 3× odcinek prosty ~80 mm | tuż za zaciskami wejściowymi |

### 1.3 Na drzwiach

Ekran 7" (płytka ESP32-S3 181 × 108 × 15 mm, wycięcie ok. 165 × 100 mm), przycisk
E-STOP Ø22, wyłącznik kluczykowy "PE STAŁE", 2–3 lampki Ø22 (zasilanie, wyjście
załączone, usterka aktywna), ewentualnie gniazdo CEE 32 A i Schuko na boku/dole obudowy.

### 1.4 Wynikowy minimalny rozmiar

* Płyta montażowa z 4 rzędami szyn (rozstaw 150 mm) + rząd zacisków = 750 mm wysokości,
  do tego strefa transformatora/rezystora ≥ 200 mm → **płyta ≥ 950 mm** przy szynach 500 mm,
  albo 3 rzędy szyn 700 mm (450 mm) + zaciski (150) + strefa T1/R (250) = **płyta ≥ 850 mm**.
* Głębokość: stycznik modułowy 70 mm + szyna/przewody; toroid 70 mm; ekran na drzwiach
  wchodzi 20–30 mm do środka → **głębokość ≥ 250 mm, wygodnie 300 mm**.

## 2. Warianty obudowy

(do uzupełnienia po researchu: oferty, ceny, wagi)

## 3. Rekomendacja

(do uzupełnienia)

## 4. Pytania do Ciebie (uszeregowane)

(do uzupełnienia)
