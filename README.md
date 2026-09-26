# BTC Cycle Planner

Applicazione desktop (Python + PyQt6) che analizza documenti sul ciclo di Bitcoin
(PDF, TXT, MD), ne estrae i parametri numerici e genera un piano di investimento.

## Cosa fa

- **Importa documenti** (menu, cartella o drag & drop) e ne estrae con regole trasparenti:
  offset del ciclo dagli halving, massimo di ciclo, scenari di minimo, power law (fair value e
  floor), ladder di accumulo, drip, riserva, DCA front-loaded, boost e kill-switch, piano di
  uscita, livelli di invalidazione, statistiche. Ogni dato mostra pagina e frammento sorgente.
- **Aggrega** i documenti: vince il più recente, i valori diversi sono segnalati come conflitti.
- **Genera il piano** con prezzo e indicatori di mercato (CoinGecko, Fear & Greed):
  cosa fare oggi, ripartizione del capitale, ladder riancorata al floor attuale, calendario DCA,
  uscita nel prossimo ciclo, scenari e stime del minimo per fonte.
- **Avvertenze critiche**: fonte unica, contenuti promozionali, stime divergenti, modelli
  incoerenti, campioni ridotti, stress test sul prezzo medio.
- Esporta il piano in HTML o Markdown. Autoupdate da GitHub Releases.

## Sviluppo

```bash
pip install -r requirements-dev.txt
python src/main.py
pytest
ruff check . --fix
```

Nuove regole di estrazione: `src/btc_cycle/core/extractors.py` (incrementare
`EXTRACTOR_VERSION` per rianalizzare i documenti già salvati).

## Release

Modificando `version.txt` su `main`, il workflow `build-installers.yml` crea installer
Windows (NSIS), macOS e Linux e pubblica la release `v<versione>`.

> Strumento educativo: non è consulenza finanziaria.
