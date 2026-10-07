# Home Assistant — odczyt i sterowanie (wersja podstawowa)

Zastępuje `HA_INTEGRACJA_ODCZYT.md` (tamten opisywał wyłącznie odczyt, bo sterowania
jeszcze nie było). Wymaga firmware **v10**.

**Zakres celowo ograniczony.** To jest wersja podstawowa, dopasowana do prowizorycznego
montażu diody nadawczej. Pełny panel biura — wizualizacje, sceny, automatyzacje — dochodzi
dopiero po montażu docelowym, bo budowanie go teraz oznaczałoby pracę do wyrzucenia.

## 1. Jak to działa — dwa niezależne tory

Kluczowa własność protokołu Gree: **pilot nie wysyła zmian, tylko komplet nastaw**.
Ramka podczerwieni niesie naraz włączenie, tryb, temperaturę, bieg i żaluzje. Nikt nie
wysyła „podnieś o stopień" — wysyła się cały nowy stan. Dlatego pełne nastawy musi pamiętać
sonda, a nie Home Assistant.

Stąd dwa tory, z których każdy wie coś innego:

```
   HA  ──HTTP──►  SONDA  ──podczerwień──►  KLIMATYZATOR
                    ▲                            │
                    └────────RS-485──────────────┘
                         (rozgłoszenie co 800 ms)
```

| Tor | Kierunek | Co niesie | Jakiej ma pewności |
|---|---|---|---|
| podczerwień | HA → jednostka | komplet nastaw | **żadnej** — nadajnik jest ślepy, nie ma potwierdzenia |
| magistrala | jednostka → HA | praca, bieg, klapy, 2 temperatury | **pełną** — to pomiar, nie deklaracja |

Nastaw (temperatura zadana, tryb) na magistrali **nie ma** — jednostka wysyła je wyłącznie
do zarejestrowanego sterownika przewodowego, którym sonda nie jest. Dlatego nastawy w HA
pochodzą z pamięci sondy: to zapis tego, co kazaliśmy, a nie odczyt z jednostki.

## 2. Magistrala pilnuje podczerwieni

Sam nadajnik IR nie daje żadnej gwarancji. Dioda może się odkleić, ktoś może zasłonić
odbiornik, ramka może przepaść. Dlatego firmware v10 **domyka pętlę sam**:

1. wysyła ramkę **trzy razy** (ramka jest idempotentna, powtórzenie nic nie psuje),
2. czeka **14 s** — tyle potrzebuje wentylator, żeby ruszyć,
3. porównuje stan z magistrali z zadanym,
4. niezgodność → powtarza komendę, **do dwóch razy**,
5. dalej niezgodność → wystawia `potwierdzenie: nie`.

Weryfikowane jest zawsze włączenie/wyłączenie, a bieg wentylatora dodatkowo w trybach
chłodzenia, grzania i wentylacji. W trybie auto i osuszania bieg jest pomijany, bo tam
jednostka zmienia go sama i niezgodność nie znaczyłaby awarii.

Pomiar z uruchomienia (zamówiony bieg wysoki): jednostka odpowiedziała w 6 s,
sonda potwierdziła w 19 s, zero ponowień.

## 3. Konfiguracja — `configuration.yaml`

### 3.1 Odczyt

```yaml
rest:
  - resource: http://192.168.0.172/stan
    scan_interval: 15
    sensor:
      - name: "Klimatyzacja biuro temperatura"
        value_template: "{{ value_json.temp_pokoj }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
      - name: "Klimatyzacja biuro wymiennik"
        value_template: "{{ value_json.temp_wymiennik }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
      - name: "Klimatyzacja biuro wentylator"
        value_template: "{{ value_json.wentylator }}"
        icon: mdi:fan
      # --- nastawy: pamięć sondy, nie odczyt z jednostki ---
      - name: "Klimatyzacja biuro nastawa sonda"
        value_template: "{{ value_json.zad_temp }}"
        unit_of_measurement: "°C"
      - name: "Klimatyzacja biuro tryb sonda"
        value_template: "{{ value_json.zad_tryb }}"
      - name: "Klimatyzacja biuro bieg sonda"
        value_template: "{{ value_json.zad_went }}"
      - name: "Klimatyzacja biuro potwierdzenie"
        value_template: "{{ value_json.potwierdzenie }}"
        icon: mdi:check-network
    binary_sensor:
      - name: "Klimatyzacja biuro pracuje"
        value_template: "{{ value_json.pracuje }}"
        device_class: running
      - name: "Klimatyzacja biuro klapy"
        value_template: "{{ value_json.klapy_otwarte }}"
        device_class: opening
      - name: "Klimatyzacja biuro sonda online"
        value_template: "{{ value_json.dostepne }}"
        device_class: connectivity
      - name: "Klimatyzacja biuro zadane wlaczenie"
        value_template: "{{ value_json.zad_wl }}"
```

### 3.2 Komendy

Każda komenda podaje tylko to, co się zmienia — resztę nastaw sonda dokłada z pamięci
i wysyła komplet.

```yaml
rest_command:
  klima_wl:
    url: "http://192.168.0.172/ustaw?wl=1"
    timeout: 15
  klima_wyl:
    url: "http://192.168.0.172/ustaw?wl=0"
    timeout: 15
  klima_temp:
    url: "http://192.168.0.172/ustaw?temp={{ temp }}"
    timeout: 15
  klima_tryb:
    url: "http://192.168.0.172/ustaw?tryb={{ tryb }}"
    timeout: 15
  klima_went:
    url: "http://192.168.0.172/ustaw?went={{ went }}"
    timeout: 15
```

### 3.3 Sterowanie

```yaml
template:
  - switch:
      - name: "Klimatyzacja biuro"
        unique_id: gree_biuro_wl
        icon: mdi:air-conditioner
        state: "{{ is_state('binary_sensor.klimatyzacja_biuro_zadane_wlaczenie','on') }}"
        availability: "{{ is_state('binary_sensor.klimatyzacja_biuro_sonda_online','on') }}"
        turn_on:
          - action: rest_command.klima_wl
          - delay: { seconds: 2 }
          - action: homeassistant.update_entity
            target:
              entity_id: binary_sensor.klimatyzacja_biuro_zadane_wlaczenie
        turn_off:
          - action: rest_command.klima_wyl
          - delay: { seconds: 2 }
          - action: homeassistant.update_entity
            target:
              entity_id: binary_sensor.klimatyzacja_biuro_zadane_wlaczenie

  - number:
      - name: "Klimatyzacja biuro nastawa"
        unique_id: gree_biuro_temp
        icon: mdi:thermometer
        unit_of_measurement: "°C"
        min: 16
        max: 30
        step: 1
        state: "{{ states('sensor.klimatyzacja_biuro_nastawa_sonda') | int(22) }}"
        availability: "{{ is_state('binary_sensor.klimatyzacja_biuro_sonda_online','on') }}"
        set_value:
          - action: rest_command.klima_temp
            data:
              temp: "{{ value | int }}"
          - delay: { seconds: 2 }
          - action: homeassistant.update_entity
            target:
              entity_id: sensor.klimatyzacja_biuro_nastawa_sonda

  - select:
      - name: "Klimatyzacja biuro tryb"
        unique_id: gree_biuro_tryb
        icon: mdi:tune
        options: "{{ ['chlodzenie','grzanie','osuszanie','wentylacja','auto'] }}"
        state: "{{ states('sensor.klimatyzacja_biuro_tryb_sonda') }}"
        availability: "{{ is_state('binary_sensor.klimatyzacja_biuro_sonda_online','on') }}"
        select_option:
          - action: rest_command.klima_tryb
            data:
              tryb: >-
                {{ {'chlodzenie':'cool','grzanie':'heat','osuszanie':'dry',
                    'wentylacja':'fan','auto':'auto'}[option] }}
          - delay: { seconds: 2 }
          - action: homeassistant.update_entity
            target:
              entity_id: sensor.klimatyzacja_biuro_tryb_sonda

      - name: "Klimatyzacja biuro bieg"
        unique_id: gree_biuro_went
        icon: mdi:fan
        options: "{{ ['auto','niski','sredni','wysoki'] }}"
        state: "{{ states('sensor.klimatyzacja_biuro_bieg_sonda') }}"
        availability: "{{ is_state('binary_sensor.klimatyzacja_biuro_sonda_online','on') }}"
        select_option:
          - action: rest_command.klima_went
            data:
              went: >-
                {{ {'auto':'auto','niski':'1','sredni':'2','wysoki':'3'}[option] }}
          - delay: { seconds: 2 }
          - action: homeassistant.update_entity
            target:
              entity_id: sensor.klimatyzacja_biuro_bieg_sonda

  - binary_sensor:
      - name: "Klimatyzacja biuro sterowanie nieskuteczne"
        unique_id: gree_biuro_alarm
        device_class: problem
        state: "{{ is_state('sensor.klimatyzacja_biuro_potwierdzenie','nie') }}"
        delay_on: { seconds: 5 }
```

Po wklejeniu: **Narzędzia deweloperskie → YAML → Przeładuj encje REST**, potem
**Przeładuj encje szablonowe**. Przy pierwszym uruchomieniu bezpieczniej zrestartować HA.

## 4. Dlaczego przełącznik pokazuje zamiar, a nie pomiar

Przełącznik `switch.klimatyzacja_biuro` bierze stan z **nastawy w sondzie**, a nie z
magistrali. To świadoma decyzja: wentylator rusza dopiero po ~10 s, więc przełącznik
oparty na pomiarze odskakiwałby po kliknięciu i wyglądał na zepsuty.

Prawdę o jednostce mówią dwie osobne encje i to na nie należy patrzeć:

| Encja | Znaczenie |
|---|---|
| `binary_sensor.klimatyzacja_biuro_pracuje` | czy jednostka **faktycznie** pracuje (magistrala) |
| `binary_sensor.klimatyzacja_biuro_sterowanie_nieskuteczne` | zapala się, gdy komenda **nie doszła** mimo ponowień |

Ta druga encja jest tu najważniejsza — to ona wyłapie odklejoną diodę albo zasłonięty
odbiornik. Bez niej sterowanie podczerwienią byłoby wiarą, a nie sterowaniem.

Automatyzacja, która o tym powiadomi:

```yaml
automation:
  - alias: "Klimatyzacja — komenda nie doszła"
    trigger:
      - trigger: state
        entity_id: binary_sensor.klimatyzacja_biuro_sterowanie_nieskuteczne
        to: "on"
    action:
      - action: persistent_notification.create
        data:
          title: "Klimatyzacja nie odpowiada"
          message: >-
            Sonda wysłała komendę trzykrotnie i powtórzyła ją dwa razy,
            a magistrala nie potwierdziła zmiany. Sprawdź diodę przy odbiorniku.
```

## 5. Ograniczenia wersji podstawowej

| Ograniczenie | Powód |
|---|---|
| brak encji `climate` | rdzeń HA nie pozwala zbudować jej z szablonu; MQTT albo HACS to komplikacja nieopłacalna przy prowizorycznym montażu |
| zmiana pilotem nie aktualizuje nastaw w HA | nastaw nie ma na magistrali; jednostka wysyła je tylko do zarejestrowanego sterownika przewodowego |
| żaluzje bez encji | sterowanie działa (`/ustaw?swing=1`), ale magistrala pokazuje tylko klapy otwarte/zamknięte, więc weryfikacja byłaby pozorna |
| jedna jednostka | pozostałe kasetony dostaną własne sondy — patrz `README.md` |

Zmiana pilotem jest widoczna tam, gdzie liczy się najbardziej: praca, bieg i temperatury
przychodzą z magistrali niezależnie od tego, kto wydał polecenie.

## 6. Adres sondy

Sonda pracuje pod `192.168.0.172`. Na routerze **zarezerwuj ten adres dla jej adresu MAC** —
inaczej po restarcie router może przydzielić inny i wszystkie encje przestaną działać.

## 7. Endpointy sondy

| Adres | Działanie |
|---|---|
| `/stan` | JSON — źródło dla wszystkich encji |
| `/` | podgląd dla człowieka w przeglądarce |
| `/ustaw?wl=1` | włącz (nastawy z pamięci) |
| `/ustaw?wl=0` | wyłącz |
| `/ustaw?temp=24` | temperatura zadana 16–30 |
| `/ustaw?tryb=cool` | `cool` / `heat` / `dry` / `fan` / `auto` |
| `/ustaw?went=2` | `auto` / `1` niski / `2` średni / `3` wysoki |
| `/ustaw?swing=1` | żaluzje |
| `/ustaw?send=1` | powtórz komplet nastaw bez zmian |

Każde wywołanie `/ustaw` wysyła **komplet nastaw** i uzbraja weryfikację przez magistralę.
Odpowiedzią jest ten sam JSON co `/stan`.
