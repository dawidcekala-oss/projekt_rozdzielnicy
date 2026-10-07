# Q11 w Home Assistant: łatka integracji Shelly

Autor: Dawid Cekała, 29.09.2026

## Po co {-}

Oficjalna integracja Shelly w Home Assistant tworzy encje pól Shelly X tylko wtedy, gdy klucz pola jest na liście w jej kodzie. Z 15 pól Q11 na tej liście są tylko fazy. Limit prądu i włącznik ładowania są tam zapisane wyłącznie dla ładowarki TopAC (kod produktu EVE01). Bez łatki Home Assistant pokazuje 19 encji: 12 fazowych i 7 systemowych. Z łatką pokazuje 33 encje.

## Co zmienia łatka {-}

| Plik | Zmiana |
|---|---|
| const.py | lista kodów produktu Ampere Point, dziś `apq11dev` |
| entity.py | pole wyboru bez napisów opcji nie wywraca encji (dotyczy trybu pracy i sygnału pojazdu) |
| number.py | limit prądu także dla Q11; nowe: limit energii, okno ładowania od i do |
| switch.py | włącznik ładowania |
| select.py | tryb ładowania (od razu, do limitu energii, w oknie godzin) |
| sensor.py | stan ładowarki, sygnał pojazdu, energia i czas sesji, energia ostatniej sesji, temperatura sterownika, usterki, wersja sterownika |
| translations | nazwy po polsku i angielsku |

Pełna różnica względem Home Assistant 2026.6.4: `latka_shelly_q11_HA2026.6.4.diff`.

## Jak działa {-}

Home Assistant najpierw szuka integracji w `C:\HomeAssistant\config\custom_components`. Kopia integracji Shelly w tym folderze zastępuje wbudowaną. Dotyczy to wszystkich urządzeń Shelly w tym Home Assistant, ale inne urządzenia działają jak dotąd, bo łatka dopisuje wyłącznie encje dla kodu `apq11dev`.

## Po aktualizacji Home Assistant {-}

Kopia zostaje w wersji 2026.6.4 i po aktualizacji może przestać pasować do nowego Home Assistant. Wtedy integracja Shelly się nie uruchomi. Po każdej aktualizacji:

```
docker exec homeassistant rm -rf /config/custom_components/shelly
docker exec homeassistant cp -r /usr/src/homeassistant/homeassistant/components/shelly /config/custom_components/shelly
python latka_shelly_q11.py C:\HomeAssistant\config\custom_components\shelly
docker restart homeassistant
```

Jeśli łatka zgłosi błąd (zmienił się kod integracji), wystarczy usunąć folder i zrestartować Home Assistant. Wróci wtedy stan sprzed łatki z 19 encjami.

## Docelowo {-}

Ta sama zmiana może trafić do oficjalnej integracji. Tak dopisano ładowarkę TopAC. Wymaga to ostatecznego kodu produktu zamiast `apq11dev`.
