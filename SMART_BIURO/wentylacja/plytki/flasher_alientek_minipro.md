# ALIENTEK Mini-Pro (programator STM32) — rola pomocnicza w projekcie

Urządzenie to **programator offline do mikrokontrolerów STM32** (chińskie oznaczenie
„Mini-Pro 脱机下载器", openedv.taobao.com) z nakładką rozszerzającą, na której są białe
gniazda typu JST-XH i powielające je rzędy złoconych szpilek (opisy: Vext / DIO / CLK /
GND / RST / SWM).

## Do czego NIE służy w tym projekcie

Jego porty to złącza do programowania procesorów (interfejs SWD) — **nie mają nic
wspólnego z RS485 ani z klimatyzatorem**. Nie potrafi symulować jednostki Gree.

## Do czego się przydał: bierny rozgałęźnik do wtyczki JST

Problem: styki małej wtyczki JST (pigtail do gniazda COM-MANUAL) są schowane w obudowie —
nie da się ich sensownie dotknąć sondą miernika. Rozwiązanie: wtyczkę pigtaila wpina się
w **4-pinowe gniazdo nakładki flashera**, a każdy styk staje się dostępny na sąsiedniej
złoconej szpilce. To pozwoliło w 2 minuty, przy biurku:

- przetestować **ciągłość wszystkich żył pigtaila** (piszczyk: szpilka ↔ drugi koniec żyły),
- potwierdzić kolejność żył we wtyczce.

## Warunek bezpieczeństwa

Podczas takiego użycia flasher **musi być odłączony od USB i niczym niezasilany** — służy
wyłącznie jako plastikowo-metalowe przedłużenie styków. Zasilony mógłby podać własne
napięcia na badane żyły.
