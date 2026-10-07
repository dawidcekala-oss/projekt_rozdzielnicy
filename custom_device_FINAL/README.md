# AMPERE POINT — custom device — WERSJA FINALNA (decyzja Z20, 2026-07-09)

Zautomatyzowana stacja testowa ładowarek AC (EVSE) z **użytkowym obciążeniem termicznym**:
moduł B to panel dziewięciu sterowanych gniazd 230 V, w które wpina się **grzejniki olejne**
(zimą grzeją warsztat energią testu), a latem — **urządzenia chłodzące** (klimatyzator/osuszacz);
gniazdo 1 zawsze zajmuje grzejnik odniesienia (stabilne kroki obciążenia). Moduł A (pomiary,
PM701E z serwami, łańcuch bezpieczeństwa) — bez zmian względem wcześniejszych wersji projektu.

## Pliki (czytaj w tej kolejności)
1. `AMPERE_POINT_custom_device_FINAL_koncepcja.pdf` — dokument główny (wydanie objaśnione,
   do czytania po kolei): elementarz pojęć, spacer po systemie, architektura, panel B,
   łańcuch bezpieczeństwa, sekwencja, firmware, etapy, kosztorys (~5,2–11,0 tys. zł),
   ryzyka R1–R8 + R25–R27, decyzja **Z20 (FINALNA)**, testy odbiorcze.
2. `AMPERE_POINT_custom_device_FINAL_schemat_elektryczny_EPLAN.pdf` — arkusze E1–E3 w konwencji
   EPLAN/IEC 60617 (E1 tor mocy; E2 łańcuch 24 V z pętlą obecności -X5; E3 panel 9 obwodów
   K11–K19 / F12.1–9 / X10.1–9 + odbiory sezonowe). Źródło: `.tex` obok.
3. `AMPERE_POINT_custom_device_FINAL_objasnienie_i_przewodnik.pdf` — objaśnienie arkuszy,
   **przewodnik uruchomienia U0–U6** (etap 0 → montaż panelu → kalibracja tabeli mocy →
   tryb letni → testy odbiorcze) oraz **poradnik EPLAN krok po kroku** (projekt AP-CD-001).
4. `AMPERE_POINT_custom_device_FINAL_wizualizacja_3D.html` — interaktywne rozmieszczenie
   (przeglądarka; przycisk **Tryb: ZIMA/LATO**, klikalne elementy, etykiety).

## Stan projektu
- Zatwierdzone i w mocy: Z1–Z6 (topologia odczepu PM701E, dwa moduły, pomiary protokołowe
  UT595/UT522, etapowanie, budżet) oraz **Z20** (moduł B grzejnikowy sezonowy — FINALNA).
- Warianty magazynowe (koncepcje v2–v7, schematy v4/v5) — odłożone; zostają w folderze
  `../custom_device/` jako opcja przyszłej rozbudowy (panel B jest wymienny bez zmian modułu A).
- Następny krok wykonawczy: **etap 0 / U2** (serwa+CP na PM701E, próbka CDSR, generator -A3
  na płytce) — bramka wydatkowa przed zakupem aparatury.

## Powiązane (poza folderem)
`../custom_device/` — historia projektu (koncepcje v1–v7, schematy v1–v5, objaśnienia,
przewodnik EPLAN v1, wizualizacje 3D v1–v3), `custom_device_inf.md` (pełny kontekst wątku);
`../Przewodnik_pomiary_stacji_ladowania.pdf` — źródło wymagań pomiarowych.
