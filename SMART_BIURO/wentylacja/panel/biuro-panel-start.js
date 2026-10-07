/*
 * biuro-panel-start.js — rozrusznik karty biuro-panel.
 *
 * Home Assistant importuje moduły z `extra_module_url` dokładnie raz, w chwili
 * otwarcia strony, i nigdy nie ponawia nieudanego importu. Jeśli w tej jednej
 * chwili serwer nie odpowiada (restart Home Assistanta, uśpiony Docker, chwilowy
 * zanik sieci, przeterminowana kopia w pamięci service workera), plik karty nie
 * dociera, element `biuro-panel` nigdy nie powstaje, a pulpit do końca sesji
 * pokazuje „Błąd konfiguracji" — w tej wersji Home Assistanta bez treści błędu.
 *
 * Ten plik jest mały, ładuje właściwą kartę i ponawia próbę, dopóki się nie uda.
 * Gdy karta w końcu się zdefiniuje, Home Assistant sam wymienia kartę-zaślepkę
 * na prawdziwą (czeka na customElements.whenDefined), więc odświeżanie strony
 * nie jest potrzebne.
 *
 * Wersja karty: ten plik czyta parametr `v` z własnego adresu i ładuje
 * `/local/biuro-panel.js?v=<ta sama wartość>`. Po zmianie karty wystarczy podbić
 * jeden numer — w `configuration.yaml` przy `biuro-panel-start.js?v=…`.
 */
const WERSJA = (() => {
  try { return new URL(import.meta.url).searchParams.get('v') || '4'; } catch (e) { return '4'; }
})();
const KARTA = '/local/biuro-panel.js?v=' + WERSJA;
const ODSTEPY_MS = [1000, 2000, 3000, 5000, 5000, 10000]; // dalej co 10 s
const LIMIT_PROB = 90;                                    // łącznie ok. 15 minut

const stan = (window.biuroPanelStart = { karta: KARTA, proby: 0, blad: null, zaladowano: null });

const czekaj = (ms) => new Promise((r) => setTimeout(r, ms));

async function ladujZPonawianiem() {
  for (let i = 0; i < LIMIT_PROB; i++) {
    stan.proby = i + 1;
    try {
      await import(KARTA);
      stan.zaladowano = new Date().toISOString();
      if (i > 0) console.info('[biuro-panel] karta załadowana za ' + (i + 1) + '. próbą');
      return;
    } catch (e) {
      stan.blad = String((e && e.message) || e);
      console.warn('[biuro-panel] import karty nie powiódł się (próba ' + (i + 1) + '): ' + stan.blad);
      // Błąd składni w samej karcie nie zniknie po ponowieniu — nie ma co próbować dalej.
      if (e instanceof SyntaxError) break;
      await czekaj(ODSTEPY_MS[Math.min(i, ODSTEPY_MS.length - 1)]);
    }
  }
  console.error('[biuro-panel] nie udało się załadować karty ' + KARTA + ' — odśwież stronę (Ctrl+F5)');
}

ladujZPonawianiem();
