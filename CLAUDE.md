# Guidelines per Claude Code

## 1. Stack e Contesto Principale
* **Linguaggio Principale:** Python 3.9+ (Focus assoluto, type hints PEP 484 obbligatori, standard OOP)[cite: 4].
* **Framework GUI:** Esclusivamente **PyQt6** o **PySide6** (Non usare Tkinter, CustomTkinter, Flet o altri framework)[cite: 4].
* **Controllo Versione & CI/CD:** GitHub Actions (Build ed esecutabili multi-piattaforma generati da PyInstaller / NSIS)[cite: 4].
* **Linguaggi Secondari (uso RARO):** PHP, JavaScript, Java. Usali solo se esplicitamente richiesto per integrazioni esterne[cite: 4].

## 2. Componenti Obbligatori dell'Interfaccia (GUI)
* **Barra dei Menu (`QMenuBar`):** Ogni finestra principale dell'applicazione deve includere una barra dei menu strutturata con[cite: 4]:
  * **Menu "Aiuto" / "Info":**
    * **Informazioni / About:** Finestra di dialogo (`QMessageBox.about`) contenente l'autore dell'applicazione e la versione corrente letta dinamicamente dal file `version.txt`[cite: 4].
    * **Controlla Aggiornamenti:** Voce di menu per avviare manualmente la verifica e il download di nuove versioni disponibili[cite: 4].
    * **Guida:** Voce che apre una finestra dedicata o un dialogo informativo con la guida all'uso dell'applicazione[cite: 4].
  * Altre voci di menu verranno specificate di volta in volta secondo le necessità del progetto[cite: 4].

## 3. Gestione Versioni, Release & Autoupdate
* **File di Versione:** Il file `version.txt` situato nella root del progetto contiene il numero di versione corrente (es. `1.0.0`)[cite: 4].
* **Trigger di Build:** Ogni volta che si apportano modifiche, fix o nuove funzionalità ai file di codice, **aggiorna sempre il numero di versione in `version.txt`** (incrementando patch o minor)[cite: 4]. Questo scatena automaticamente la build degli installer via `.github/workflows/build-installers.yml`[cite: 4].
* **Sistema di Autoupdate:**
  * **Verifica Automatica all'Avvio:** L'applicazione deve verificare in background (tramite API GitHub Releases o endpoint dedicato) la presenza di nuove versioni confrontando la versione remota con quella locale in `version.txt`[cite: 4].
  * **Notifica e Download:** Se disponibile una nuova release, mostrare un dialogo informativo (`QMessageBox` o dialogo custom con changelog) chiedendo conferma all'utente[cite: 4].
  * **Installazione / Sostituzione:** Gestire il download dell'installer/binario aggiornato ed eseguire il processo di aggiornamento/riavvio senza bloccare l'esperienza utente[cite: 4].

## 4. Standard di Sviluppo GUI & Architettura Qt
* **Threading/Asincronia:** NON eseguire mai operazioni I/O, chiamate API di rete, query pesanti o controllo aggiornamenti nel main thread della GUI[cite: 4]. Usa sempre `QThread` (o `QThreadPool`/`QRunnable`) e i segnali (`pyqtSignal` / `Signal`) per comunicare con l'interfaccia[cite: 4].
* **Separazione Architetturale:** Separa rigorosamente la logica della GUI (layout, widget, segnali) dalla logica di business/backend e dal modulo di aggiornamento (`updater`)[cite: 4].
* **Design & Styling (QSS):**
  * Applica griglie di spaziatura coerenti (multipli di 4px/8px per padding e margini).
  * Palette coerenti ad alto contrasto (WCAG AA compliant) per temi scuri/chiari, evitando gradienti casuali o pulsanti disallineati.
  * Nessun elemento UI deve sembrare un widget di sistema grezzo non stilizzato: usa fogli di stile centralizzati (`styles.qss` o modulo dedicato).
* **Gestione Errori:** Intercetta le eccezioni di rete o I/O silenziosamente in background o tramite dialoghi chiari (`QMessageBox.warning`/`QMessageBox.critical`) se l'azione è manuale, impedendo qualsiasi crash improvviso[cite: 4].

## 5. Comandi di Sviluppo & Test
* **Esecuzione App:** `python src/main.py`[cite: 4]
* **Test Suite:** `pytest` (priorità alla logica interna e modelli)[cite: 4]
* **Linter / Formatting:** `ruff check . --fix` (in alternativa `black .` / `flake8 .`)[cite: 4]
* **Dipendenze:** `pip freeze > requirements.txt`[cite: 4]

## 6. Regole Operative per l'Agente
* **Lingua:** Rispondi e inserisci commenti nel codice sempre in **italiano**[cite: 4].
* **Stile Risposte:** Diretto, asciutto, orientato al codice e ai comandi. Evita preamboli e conclusioni superflue[cite: 4].
* **Autonomia e Versionamento:** Aggiorna `version.txt` a ogni modifica funzionale o strutturale[cite: 4].
* **Gestione Git e Branch:** Completate e verificate le modifiche su un branch, esegui autonomamente push e merge su `main` senza richiedere conferme ridondanti[cite: 4].
* **Pulizia Workspace:** Non generare file `.md` effimeri di recap, note sparse o copie `.bak` se non espressamente richiesto[cite: 4].

## 7. Integrazione Plugin, Skill & Server MCP

### Strumenti Attivi e Obbligatori:
* **claude-mem:** Salva contesto, bug risolti e decisioni architetturali direttamente nella memoria del plugin tra una sessione e l'altra (`mem-search`, `learn-codebase`)[cite: 4].
* **superpowers:**
  * Applica `test-driven-development` per moduli core e logica di business.
  * Usa `systematic-debugging` in caso di bug o crash Qt.
  * Prima di modifiche strutturali, stila il piano d'azione (file target, segnali/slot, thread worker)[cite: 4].
* **impeccable & frontend-design:**
  * Applica le loro regole di design system, accessibilità, proporzioni e palette esclusivamente a **QSS (Qt Style Sheets)** e layout PyQt/PySide[cite: 4].
  * Vietata l'introduzione di dipendenze o runtime web (HTML/CSS grezzo non interpretato da Qt)[cite: 4].
* **21st-ui:**
  * Usalo solo per ricercare riferimenti visivi, layout di card, sidebar o tabelle moderne.
  * Traduci i pattern trovati direttamente in widget Qt e classi QSS corrispondenti.
* **Context7:**
  * Interrogalo per verificare firme esatte di metodi, enumerazioni o differenze tra versioni di PyQt6/PySide6 prima di ipotizzare API deprecate o inesistenti.

### Strumenti Esclusi (Blacklist):
* **Ignora categoricamente:** Plugin di contabilità/finanza (`variance-analysis`, `journal-entry`, `sox-testing`, ecc.), tool di editing Office (`docx`, `xlsx`, `pptx`) e comandi della suite **ponytail** (non forzare l'anti-pattern del minimalismo spinto a discapito della modularità OOP e della robustezza del codice).

## Skill esterne
* **find-skills:** Usala solo se chiedo esplicitamente di cercare o installare una skill. Prima di proporre un'installazione verifica install count (>1K) e fonte; non usare mai `-y` né `-g` senza mia conferma esplicita.