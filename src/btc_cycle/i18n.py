"""Traduzioni: le chiavi sono i testi italiani; ``tr`` restituisce l'inglese se la lingua è "en"."""

from __future__ import annotations

LANGUAGES = {"it": "Italiano", "en": "English"}
_lang = "it"

EN = {
    # menu
    "&File": "&File", "&Dati": "&Data", "&Strumenti": "&Tools", "&Aiuto": "&Help",
    "Importa documenti…": "Import documents…", "Importa cartella…": "Import folder…",
    "Esporta piano (HTML)…": "Export plan (HTML)…", "Esporta piano (Markdown)…": "Export plan (Markdown)…",
    "Esci": "Quit", "Aggiorna dati di mercato": "Refresh market data", "Genera piano": "Generate plan",
    "Rianalizza tutti i documenti": "Re-analyze all documents",
    "Rimuovi documento selezionato": "Remove selected document", "Apri cartella dati": "Open data folder",
    "Documenti e parametri…": "Documents and parameters…", "Lingua": "Language",
    "Guida": "Guide", "Controlla aggiornamenti": "Check for updates", "Informazioni": "About",
    # schede e tabelle
    "Piano": "Plan", "Grafico": "Chart", "Documenti": "Documents", "Parametri": "Parameters",
    "Rimuovi": "Remove", "Rianalizza tutto": "Re-analyze all",
    "Suggerimento: puoi trascinare PDF/TXT/MD nella finestra.": "Tip: you can drag PDF/TXT/MD files into the window.",
    "Titolo": "Title", "Data": "Date", "Fonte": "Source", "Insight": "Insights", "Flag": "Flags",
    "Categoria": "Category", "Parametro": "Parameter", "Valore": "Value", "Pag.": "Page",
    "Evidenza": "Evidence", "Conflitti": "Conflicts",
    "Per ogni parametro vale il documento più recente; i valori diversi di altri documenti "
    "sono indicati come conflitti.": "The most recent document wins for each parameter; differing "
    "values from other documents are shown as conflicts.",
    # form piano
    "n/d": "n/a", "Capitale e mercato": "Capital and market", "Aggiorna dati di mercato ": "",
    "Capitale": "Capital", "Valuta": "Currency", "USD per 1 unità": "USD per 1 unit",
    "Prezzo BTC (USD)": "BTC price (USD)", "Strategia": "Strategy", "da profilo": "from profile",
    "Riancora ladder al floor attuale": "Re-anchor ladder to current floor",
    "Drip lento (metà)": "Slow drip (half)", "Profilo": "Profile",
    "Quota finestra minimo": "Bottom-window share", "Indicatori (opzionali)": "Indicators (optional)",
    "MA 200 giorni": "200-day MA", "Massimo 200 giorni": "200-day high",
    "Minimo chiusura ciclo": "Cycle closing low", "Esporta HTML": "Export HTML",
    "Esporta Markdown": "Export Markdown",
    "<p style='color:#6b7280'>Importa i documenti e premi <b>Genera piano</b>.</p>":
        "<p style='color:#6b7280'>Import the documents and press <b>Generate plan</b>.</p>",
    # messaggi
    "Caricamento knowledge base…": "Loading knowledge base…", "Errore: {e}": "Error: {e}",
    "Salvataggio": "Saving", "Impossibile salvare: {e}": "Unable to save: {e}",
    "Impossibile leggere i dati salvati:\n{error}": "Unable to read the saved data:\n{error}",
    "Pronto.": "Ready.", "Documenti (*.pdf *.txt *.md);;PDF (*.pdf);;Tutti i file (*)":
        "Documents (*.pdf *.txt *.md);;PDF (*.pdf);;All files (*)",
    "Importa documenti": "Import documents", "Importa cartella": "Import folder",
    "Analisi dei documenti…": "Analyzing documents…", "Importazione": "Import",
    "Importati {added} nuovi documenti ({updated} aggiornati).": "Imported {added} new documents ({updated} updated).",
    "\n\nErrori:\n": "\n\nErrors:\n", "Analisi: {name}": "Analyzing: {name}",
    "Rimuovere «{title}»?": "Remove “{title}”?", "Documenti rianalizzati.": "Documents re-analyzed.",
    "Rianalisi": "Re-analysis", "Documenti: {d} · Parametri: {p}": "Documents: {d} · Parameters: {p}",
    "Download dati di mercato…": "Downloading market data…", "Dati di mercato": "Market data",
    "Download non riuscito:\n{errors}": "Download failed:\n{errors}",
    "Dati di mercato aggiornati": "Market data updated", " (parziali)": " (partial)",
    "Piano generato.": "Plan generated.", "Esporta": "Export", "Genera prima un piano.": "Generate a plan first.",
    "Esporta piano": "Export plan", "Esportato: {path}": "Exported: {path}",
    "Aggiornamenti": "Updates",
    "Nessun aggiornamento: la versione {v} è la più recente.": "No update: version {v} is the latest.",
    "Controllo non riuscito:\n{err}": "Check failed:\n{err}", "Download {name}…": "Downloading {name}…",
    "Aggiornamento": "Update",
    "Scaricato in:\n{path}\n\nChiudi l'app e sostituisci l'eseguibile con quello nuovo.":
        "Downloaded to:\n{path}\n\nClose the app and replace the executable with the new one.",
    "Download non riuscito:\n{err}": "Download failed:\n{err}",
    "Informazioni su {app}": "About {app}", "Versione {v}": "Version {v}", "Autore: {a}": "Author: {a}",
    "Analizza documenti sul ciclo di Bitcoin e genera un piano di investimento.":
        "Analyzes documents on the Bitcoin cycle and generates an investment plan.",
    "Strumento educativo, non consulenza finanziaria.": "Educational tool, not financial advice.",
    "La lingua cambierà al prossimo avvio dell'applicazione.": "The language will change the next time you start the application.",
    # dialoghi
    "Guida — {app}": "Guide — {app}", "Aggiornamento disponibile": "Update available",
    "È disponibile la versione {new} (installata: {old}).\nVuoi scaricarla e installarla ora?":
        "Version {new} is available (installed: {old}).\nDo you want to download and install it now?",
    # grafico
    "Genera un piano per vedere livelli e finestre della strategia.":
        "Generate a plan to see the strategy's levels and windows.",
    "Aggiorna storico": "Refresh history", "Reimposta vista": "Reset view",
    "Scala logaritmica": "Logarithmic scale",
    "Fonti: {docs}. Livelli e finestre sono stime di terzi, non previsioni.":
        "Sources: {docs}. Levels and windows are third-party estimates, not forecasts.",
    "Download storico…": "Downloading history…", "storico aggiornato {t}": "history updated {t}",
    "live {t}": "live {t}", "errore di rete ({err})": "network error ({err})",
    "In attesa dei dati di mercato…": "Waiting for market data…",
    "dentro la ladder {n}": "inside ladder {n}", "gradino {n} della ladder: {d:+.1f}%": "ladder rung {n}: {d:+.1f}%",
    "rally dal minimo {low}: {pct:+.0f}% (mediana rally falliti +{med:.0f}%, 15 casi, solo contesto)":
        "rally from low {low}: {pct:+.0f}% (median failed rally +{med:.0f}%, 15 cases, context only)",
    "Fair value power law": "Power law fair value", "Floor power law": "Power law floor",
    "Prezzo {p}": "Price {p}", "Finestra di minimo": "Bottom window", "Minimo stimato": "Estimated bottom",
    "Ladder {n} · {rng} · {pct}%": "Ladder {n} · {rng} · {pct}%",
}

GUIDE_EN = """
<h2>{app} — Guide</h2>
<p>The program reads documents (PDF, TXT, MD) on the Bitcoin cycle, the power law and accumulation
strategies, extracts their numeric parameters and combines them with market data to generate an
investment plan.</p>

<h3>1. Import the documents</h3>
<ul>
<li><b>File → Import documents…</b> (Ctrl+O), <b>Import folder…</b> or drag the files into the window.</li>
<li><b>Tools → Documents and parameters…</b> shows, for each file, the source, date, flags (e.g.
promotional content) and every extracted item with page and text excerpt.</li>
<li>Documents already imported are recognized (hash) and not duplicated.</li>
</ul>

<h3>2. Check the parameters</h3>
<p>The <b>Parameters</b> tab shows the effective strategy: the most recent document wins for each
parameter; differing values from other documents are flagged as conflicts. If a parameter is
missing, the plan uses a default declared in the report.</p>

<h3>3. Generate the plan</h3>
<ul>
<li>Enter capital, currency and exchange rate, BTC price (or <b>Refresh market data</b>, F5).</li>
<li>Optional indicators (Fear &amp; Greed, MA200, 200-day high, VIX, cycle closing low) enable boosts,
the kill-switch and the "new low" rule.</li>
<li><b>Bottom-window share</b>: part of the capital devoted to ladder + drip + reserve; the rest goes
into the extended front-loaded DCA.</li>
<li><b>Re-anchor ladder to floor</b>: shifts the price zones in proportion to today's power-law floor,
as stated in the source document.</li>
</ul>

<h3>4. Chart</h3>
<p>The <b>Chart</b> tab shows the BTC price (refreshed every 60 s) with the ladder bands, the power-law
fair value and floor, invalidation levels, MA200 and the bottom window. Use the checkbox to switch
between linear and logarithmic scale.</p>

<h3>5. Read the warnings</h3>
<p>The <b>Warnings</b> section flags single sources, promotional content, diverging estimates, small
statistical samples and a stress test. Do not ignore it.</p>

<p><i>Educational tool: not financial advice.</i></p>
"""


def set_lang(code: str) -> None:
    global _lang
    _lang = code if code in LANGUAGES else "it"


def get_lang() -> str:
    return _lang


def tr(text: str) -> str:
    return EN.get(text, text) if _lang == "en" else text
