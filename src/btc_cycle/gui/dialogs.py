"""Dialoghi: guida e proposta di aggiornamento."""

from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QTextBrowser, QVBoxLayout

from .. import APP_NAME
from ..i18n import GUIDE_EN, get_lang, tr
from ..updater import ReleaseInfo

GUIDE_HTML = f"""
<h2>{APP_NAME} — Guida</h2>
<p>Il programma legge documenti (PDF, TXT, MD) su ciclo di Bitcoin, power law e strategie di
accumulo, ne estrae i parametri numerici e li combina con i dati di mercato per generare un
piano di investimento.</p>

<h3>1. Importa i documenti</h3>
<ul>
<li><b>File → Importa documenti…</b> (Ctrl+O), <b>Importa cartella…</b> oppure trascina i file
nella finestra.</li>
<li><b>Strumenti → Documenti e parametri…</b> mostra, per ogni file, la fonte, la data, i flag (es. contenuto
promozionale) e ogni informazione estratta con pagina e frammento di testo.</li>
<li>I documenti già importati vengono riconosciuti (hash) e non duplicati.</li>
</ul>

<h3>2. Controlla i parametri</h3>
<p>La scheda <b>Parametri</b> (in Strumenti) mostra la strategia effettiva: per ogni parametro vince il
documento più recente; i valori diversi di altri documenti sono segnalati come conflitti.
Se un parametro manca, il piano usa un valore predefinito dichiarato nel report.</p>

<h3>3. Genera il piano</h3>
<ul>
<li>Inserisci capitale, valuta e cambio, prezzo BTC (o <b>Aggiorna dati di mercato</b>, F5).</li>
<li>Gli indicatori opzionali (Fear &amp; Greed, MA200, massimo 200 gg, VIX, minimo di chiusura
del ciclo) attivano boost, kill-switch e la regola del "nuovo minimo".</li>
<li><b>Quota finestra di minimo</b>: parte del capitale dedicata a ladder + drip + riserva; il
resto va nel DCA esteso front-loaded.</li>
<li><b>Riancora ladder al floor</b>: sposta le zone di prezzo in proporzione al floor power law
di oggi, come indicato dal documento sorgente.</li>
</ul>

<h3>4. Grafico</h3>
<p>La scheda <b>Grafico</b> mostra il prezzo BTC (aggiornato ogni 60 s) con le fasce della ladder,
fair value e floor della power law, livelli di invalidazione, MA200 e finestra di minimo. La
casella permette di passare tra scala lineare e logaritmica. Con il click sinistro su un punto
traccia le linee di prezzo e data (l'etichetta mostra lo scarto dal prezzo attuale); con il click
destro le rimuove. <b>Mostra uscite</b> estende il grafico fino alle vendite programmate (date,
percentuali, finestra di picco e obiettivo dichiarato). <b>Esporta immagine…</b> e <b>Copia</b>
salvano o copiano il grafico (con stato e fonti) in PNG per condividerlo.</p>

<h3>5. Leggi le avvertenze</h3>
<p>La sezione <b>Avvertenze</b> segnala fonti uniche, contenuti promozionali, stime divergenti,
campioni statistici ridotti e uno stress test. Non ignorarla.</p>

<h3>Estendere l'analisi</h3>
<p>Le regole di estrazione sono in <code>src/btc_cycle/core/extractors.py</code>. Quando
cambia <code>EXTRACTOR_VERSION</code> i documenti salvati vengono rianalizzati automaticamente.</p>

<p><i>Strumento educativo: non è consulenza finanziaria.</i></p>
"""


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Guida — {app}").format(app=APP_NAME))
        self.resize(640, 620)
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setHtml(GUIDE_EN.format(app=APP_NAME) if get_lang() == "en" else GUIDE_HTML)
        layout.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


def ask_update(parent, release: ReleaseInfo, local_version: str) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(tr("Aggiornamento disponibile"))
    box.setText(tr("È disponibile la versione {new} (installata: {old}).\n"
                   "Vuoi scaricarla e installarla ora?").format(new=release.version, old=local_version))
    if release.notes:
        box.setDetailedText(release.notes)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes
