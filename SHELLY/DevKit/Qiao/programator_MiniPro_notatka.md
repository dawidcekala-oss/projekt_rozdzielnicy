# Programator ALIENTEK MiniPro: co wiemy i czego brakuje (2026-09-28)

## Czego chce fabryka

Inżynier fabryki (Corey, Qiao) prosi o **dwa kody z okna programu klienta programatora**:

| Pole w programie (chiński) | Znaczenie | Przykład z ich zrzutu (NIE nasz) |
| --- | --- | --- |
| 设备远程序列号 | zdalny numer seryjny programatora | `C4188E693BE31196F44FA951` |
| 设备唯一SN | unikatowy numer urządzenia | `FF362E312DFF2D32312F3D483846512D3745502C` |

Fabryka generuje zaszyfrowany plik firmware **przywiązany do tych numerów**. Plik da się wgrać tylko tym jednym programatorem, przez program „klient plików zdalnych” (正点原子 MiniPro 脱机下载器远程文件客户端, wersja na zrzucie 2.7). Program pokazuje też licznik dozwolonych wgrań (可烧录次数, na zrzucie 5000) i kod kroczący (当前滚码值).

## Co ustaliliśmy o naszym programatorze

- Po wpięciu w USB laptopa zgłasza się jako urządzenie HID: `USB\VID_0483&PID_CCCC`, opis z magistrali **„Downloader-Mini-pr0”**, numer seryjny w opisie USB „STM32”.
- To jest ALIENTEK (正点原子) Mini-Pro 脱机下载器, czyli dokładnie ten typ, o który pyta fabryka.
- Dwa kody **nie są** w opisie USB. Odczytuje je tylko program klienta producenta (własny protokół HID).

## Jak zdobyć kody

1. Zainstalować program klienta ALIENTEK. Źródła:
   - dokumentacja produktu: http://www.openedv.com/docs/tool/programmer/index.html (strona `mini-pro`),
   - paczka na Baidu Pan (wymaga konta Baidu): https://pan.baidu.com/s/1Y6JjXBNqEB3je0oHu22TwA kod `y2r9`,
   - **najprościej: poprosić Corey/Nathana na WeChat o instalator „MiniPro远程文件客户端 V2.7”** (oni go używają).
2. Podłączyć programator, uruchomić program, wybrać 设备: MiniPro, kliknąć 刷新信息 (odśwież informacje).
3. Przepisać oba pola z czerwonej ramki i zapisać do pliku `pliki_do_wysłania\programator_MiniPro_kody.txt`.

## Do czego to służy u nas

- Q20 (3,7 kW): wgranie nowego firmware sterownika przez złącze programowania płyty.
- Q11 z modułem Shelly: droga zapasowa do aktualizacji sterownika, gdyby fabryka nie zgodziła się przekazać zwykłego pliku .bin do aktualizacji przez moduł (pytanie 9 w dokumentacji).

## Plik od fabryki (dopisane 2026-10-05)

- W folderze `Q11_firmware` jest plik `X2BL311O_V22(KPCBV4_ZPCBV4_LCDV8).ATK`, 78 608 B. Nazwa wskazuje wersję programu V22 dla płyty sterującej V4, płyty głównej V4 i wyświetlacza V8.
- To zaszyfrowana paczka dla programatora MiniPro (ATK = ALIENTEK, 正点原子), przywiązana do naszego programatora. Treść nieczytelna: brak tekstów, zawartość wygląda na losową.
- Nie odszyfrowujemy jej. Do wgrania służy klient MiniPro i programator. Do analizy albo do aktualizacji przez moduł Shelly potrzebny jest zwykły plik .bin od fabryki; to pytanie Q9 z 30.09, nadal bez odpowiedzi.
