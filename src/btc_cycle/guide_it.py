"""Testo della guida PDF (italiano). Segnaposto: {app}, {version}."""

GUIDE_IT = """
<h1>{app}</h1>
<p class="sub">Guida completa all'uso e al significato delle voci — versione {version}</p>
<p class="note"><b>Avvertenza.</b> Il programma è uno strumento educativo. Non fornisce consulenza
finanziaria, non prevede i prezzi e non garantisce alcun risultato. Tutti i livelli, le date e le
percentuali provengono dai documenti che importi (stime di terzi) e dai dati di mercato scaricati:
verificali sempre con fonti indipendenti prima di decidere. Investi solo capitale che puoi
lasciare fermo per anni.</p>

<h2>Indice</h2>
<ol>
<li>A cosa serve e come ragiona</li>
<li>Avvio rapido in 6 passi</li>
<li>Panoramica della finestra</li>
<li>Importare e gestire i documenti</li>
<li>Scheda Piano: i campi da compilare</li>
<li>Come leggere il piano generato</li>
<li>Scheda Grafico</li>
<li>Menu, lingua, aggiornamenti e dati salvati</li>
<li>Glossario</li>
<li>Limiti, avvertenze e risoluzione dei problemi</li>
</ol>

<h2>1. A cosa serve e come ragiona</h2>
<p>Molti analisti pubblicano strategie sul ciclo di Bitcoin in PDF (tempi dagli halving, zone di
acquisto, percentuali di capitale, piani di vendita). {app} fa tre cose:</p>
<ol>
<li><b>Legge</b> i documenti (PDF, TXT, MD) ed <b>estrae i parametri numerici</b> con regole fisse e
trasparenti. Ogni valore estratto conserva pagina e frammento di testo da cui deriva.</li>
<li><b>Aggrega</b> i documenti: per ogni parametro vale il documento più recente; i valori diversi
degli altri documenti vengono segnalati come conflitti.</li>
<li><b>Combina</b> i parametri con prezzo e indicatori di mercato correnti e con il tuo capitale per
produrre un <b>piano operativo</b> (cosa fare oggi, quanto, a quali livelli e quando) e un
<b>grafico</b> con prezzo, livelli e finestre temporali.</li>
</ol>
<p>Il programma non prende decisioni al posto tuo: applica meccanicamente le regole dei documenti
e, in più, ti mostra le <b>avvertenze critiche</b> (fonte unica, contenuti promozionali, stime
divergenti, campione statistico minimo, stress test).</p>
<p><b>Se un parametro non è presente nei documenti</b> il piano usa un valore predefinito e lo indica
nella sezione «Fonti e parametri usati» con la dicitura «predefinito».</p>

<h2>2. Avvio rapido in 6 passi</h2>
<ol>
<li><b>Importa i documenti</b>: menu <i>File → Importa documenti…</i> (Ctrl+O), <i>Importa
cartella…</i>, oppure trascina i file nella finestra.</li>
<li>(Facoltativo) apri <i>Strumenti → Documenti e parametri…</i> per controllare cosa è stato
estratto e se ci sono conflitti.</li>
<li>Nella scheda <b>Piano</b> inserisci <b>Capitale</b> e <b>Valuta</b>.</li>
<li>Premi <b>Aggiorna dati di mercato</b> (F5): compila prezzo, cambio, MA 200, massimo 200 giorni,
minimo di chiusura del ciclo e Fear &amp; Greed. Il VIX va inserito a mano (facoltativo).</li>
<li>Scegli <b>Profilo</b> e opzioni di strategia, poi premi <b>Genera piano</b> (Ctrl+G).</li>
<li>Leggi il piano a destra (parti da «Cosa fare adesso» e da «Avvertenze»), apri la scheda
<b>Grafico</b> e, se vuoi, esporta il piano (HTML/Markdown) o l'immagine del grafico.</li>
</ol>

<h2>3. Panoramica della finestra</h2>
<table>
<tr><th>Elemento</th><th>Contenuto</th></tr>
<tr><td>Barra dei menu</td><td><b>File</b> (importazione, esportazione, esci), <b>Dati</b> (mercato,
piano, rianalisi, rimozione, cartella dati), <b>Strumenti</b> (documenti e parametri, lingua),
<b>Aiuto</b> (guida, aggiornamenti, informazioni).</td></tr>
<tr><td>Scheda Piano</td><td>A sinistra i campi di input; a destra il report del piano generato.</td></tr>
<tr><td>Scheda Grafico</td><td>Prezzo BTC con livelli, fasce e finestre della strategia.</td></tr>
<tr><td>Barra di stato</td><td>Messaggi di stato e, a destra, il numero di documenti e di parametri
presenti nella knowledge base.</td></tr>
</table>
<p>Le operazioni lunghe (importazione, download dei dati, controllo aggiornamenti) girano in
background: l'interfaccia resta utilizzabile. In caso di errore di rete compare un avviso, ma
l'applicazione non si blocca.</p>

<h2>4. Importare e gestire i documenti</h2>
<h3>4.1 Formati e importazione</h3>
<ul>
<li><b>Formati:</b> PDF con testo selezionabile, TXT, MD. Un PDF scansionato (solo immagini)
non è leggibile: serve un OCR esterno.</li>
<li><b>Come:</b> <i>File → Importa documenti…</i>, <i>Importa cartella…</i> (include le
sottocartelle) o trascinamento nella finestra.</li>
<li><b>Duplicati:</b> ogni file ha un'impronta (hash): se lo reimporti viene riconosciuto e
aggiornato, non duplicato. Il messaggio finale indica quanti documenti sono nuovi e quanti
aggiornati.</li>
</ul>
<h3>4.2 Cosa viene estratto</h3>
<p>Le regole cercano nel testo (in inglese e nei formati usati dagli autori) questi gruppi di
informazioni:</p>
<table>
<tr><th>Gruppo</th><th>Esempi di parametri</th></tr>
<tr><td>Ciclo</td><td>Mesi dall'halving al picco e al minimo, finestra di accumulo, giorni
halving→picco, massimo di ciclo (prezzo e data), mesi dal massimo al minimo nei cicli passati,
drawdown e rendimenti storici, scenari di minimo, data del prossimo halving.</td></tr>
<tr><td>Power law</td><td>Esponente, ancora del fair value («prezzo X% sotto il fair value alla data
Y»), floor (banda inferiore), rotture storiche del floor.</td></tr>
<tr><td>Accumulo</td><td>Ripartizione ladder/drip/riserva, zone della ladder, drip giornaliero (e
lento), quota per il «flush», anti-miss settimanale, finestra di accumulo.</td></tr>
<tr><td>DCA</td><td>Durata, front-load per blocchi di mesi, boost (drawdown, Fear &amp; Greed, VIX),
tetto mensile dei boost, kill-switch sulla MA200.</td></tr>
<tr><td>Uscita</td><td>Vendite programmate (mesi dopo halving), quota da tenere per sempre,
RSI settimanale di conferma, numero minimo di segnali di euforia.</td></tr>
<tr><td>Livelli</td><td>Livello di invalidazione rialzista e ribassista, livelli citati
(supporti/obiettivi).</td></tr>
<tr><td>Statistiche e stagionalità</td><td>Rally falliti, pullback mediani, rendimenti mediani per
mese.</td></tr>
<tr><td>Allocazione</td><td>Quota BTC/ETH nei primi mesi, altcoin, regole come «nessuna leva» o
«mai comprare nei rally».</td></tr>
</table>
<h3>4.3 Controllo dei risultati (Strumenti → Documenti e parametri…)</h3>
<ul>
<li><b>Documenti:</b> titolo, data, fonte (autore o sito), numero di insight estratti, flag.
Selezionando un documento in basso compaiono gli insight: categoria, parametro, valore, pagina ed
<b>evidenza</b> (il frammento di testo originale). Passa il mouse sulla cella per il testo completo.</li>
<li><b>Flag:</b> «promozionale» (il documento porta a contenuti a pagamento: i track record citati sono
auto-dichiarati), «disclaimer: non è consulenza finanziaria», «campioni statistici ridotti
dichiarati».</li>
<li><b>Parametri:</b> la strategia effettiva. Per ogni parametro: valore usato, documento di
origine, data e <b>Conflitti</b> (valori diversi proposti da altri documenti). Vince sempre il
documento più recente.</li>
<li><b>Rimuovi</b> elimina il documento selezionato; <b>Rianalizza tutto</b> riapplica le regole di
estrazione a tutti i documenti salvati (utile dopo un aggiornamento del programma).</li>
</ul>
<p class="tip">Se un valore estratto non corrisponde a ciò che leggi nel PDF, l'evidenza mostra
come è stato letto: puoi così capire se il documento usa una formulazione che le regole non
riconoscono. In quel caso il piano ricade sul valore predefinito.</p>

<h2>5. Scheda Piano: i campi da compilare</h2>
<h3>5.1 Capitale e mercato</h3>
<table>
<tr><th>Campo</th><th>Significato</th></tr>
<tr><td>Capitale</td><td>Importo totale che intendi destinare al piano, nella valuta scelta. Deve
essere denaro che puoi lasciare fermo 4+ anni, separato dal fondo di emergenza.</td></tr>
<tr><td>Valuta</td><td>EUR o USD. Il piano ragiona in dollari (i prezzi dei documenti sono in USD) e
converte con il cambio indicato.</td></tr>
<tr><td>USD per 1 unità</td><td>Quanti dollari vale 1 unità della valuta del capitale (es. 1,17 per
EUR). Con USD è bloccato a 1. Si aggiorna con i dati di mercato.</td></tr>
<tr><td>Prezzo BTC (USD)</td><td>Prezzo di riferimento per tutti i calcoli. Si compila con
«Aggiorna dati di mercato» oppure a mano.</td></tr>
<tr><td>Aggiorna dati di mercato</td><td>Scarica da CoinGecko prezzo, cambio USD/EUR e 365 giorni di
chiusure giornaliere (da cui calcola MA 200, massimo 200 giorni e minimo di chiusura del ciclo) e
l'indice Fear &amp; Greed da alternative.me. Se un servizio non risponde i campi restano invariati e
compare un avviso.</td></tr>
<tr><td>Data</td><td>Data di analisi: determina in che punto del ciclo ti trovi. Di norma è oggi, ma
puoi simulare altre date.</td></tr>
</table>
<h3>5.2 Strategia</h3>
<table>
<tr><th>Campo</th><th>Significato</th></tr>
<tr><td>Profilo</td><td><b>Prudente</b>: 40% del capitale nella «finestra di minimo», nessuna altcoin/ETH.
<b>Bilanciato</b>: 50%, fino al 20% altcoin e 10% ETH. <b>Aggressivo</b>: 60%, fino al 30% altcoin e 20% ETH.
I limiti effettivi sono il minore tra profilo e documenti.</td></tr>
<tr><td>Quota finestra minimo</td><td>Percentuale del capitale dedicata a ladder + drip + riserva
(la «finestra di minimo»). «Da profilo» usa il valore del profilo. Il resto va nel DCA esteso.</td></tr>
<tr><td>Riancora ladder al floor attuale</td><td>Le zone di prezzo della ladder sono scritte per un
floor della power law di una certa data. Con questa opzione vengono spostate in proporzione al floor
di oggi (fattore mostrato nel piano). Se disattivata, restano ai prezzi del documento.</td></tr>
<tr><td>Drip lento (metà)</td><td>Dimezza la percentuale giornaliera del drip (es. da 1% a 0,5% del
capitale al giorno), allungando la durata dell'acquisto.</td></tr>
</table>
<h3>5.3 Indicatori (opzionali)</h3>
<p>Servono ad attivare le regole condizionali dei documenti. Se un indicatore è «n/d» la relativa
regola non è valutabile e il piano lo segnala.</p>
<table>
<tr><th>Campo</th><th>A cosa serve</th></tr>
<tr><td>Fear &amp; Greed</td><td>Indice di sentiment 0–100 (0 = paura estrema). Se sotto la soglia del documento
(di norma 25) attiva un boost del DCA.</td></tr>
<tr><td>MA 200 giorni</td><td>Media mobile semplice a 200 giorni delle chiusure. Serve al kill-switch: se il
prezzo supera la MA200 di oltre una certa percentuale (di norma 40%) i boost si sospendono.</td></tr>
<tr><td>Massimo 200 giorni</td><td>Il massimo di chiusura degli ultimi 200 giorni. Se il prezzo è a una
distanza dal massimo pari o superiore alla soglia (di norma 20%) si attiva un boost.</td></tr>
<tr><td>VIX</td><td>Indice di volatilità dell'azionario USA. Se sopra la soglia (di norma 25) si attiva un
boost. Non viene scaricato automaticamente.</td></tr>
<tr><td>Minimo chiusura ciclo</td><td>Il minimo di chiusura giornaliera dopo il massimo dell'anno. Un
gradino della ladder scatta solo con una chiusura giornaliera sotto questo livello («nuovo minimo»),
non con una candela intraday.</td></tr>
</table>
<h3>5.4 Pulsanti</h3>
<ul>
<li><b>Genera piano</b> (Ctrl+G): calcola e mostra il report. Si ricalcola anche quando importi
documenti o aggiorni il mercato.</li>
<li><b>Esporta HTML / Markdown</b>: salva il report in un file (anche da <i>File</i>).</li>
</ul>

<h2>6. Come leggere il piano generato</h2>
<p>Il report è diviso in sezioni, sempre nello stesso ordine. Alcune compaiono solo se
pertinenti alla fase del ciclo.</p>
<h3>6.1 Cosa fare adesso</h3>
<p>Elenco operativo sintetico generato dalle regole: acquisti dei gradini attivi, stato del drip,
promemoria anti-miss, prima rata del DCA con l'eventuale boost, oppure «nessun acquisto» se sei in
fase di rialzo o di picco. È la sezione da leggere per prima.</p>
<h3>6.2 Situazione di mercato e ciclo</h3>
<table>
<tr><th>Voce</th><th>Significato</th></tr>
<tr><td>Ultimo halving</td><td>Data dell'ultimo dimezzamento della ricompensa dei blocchi, giorni e mesi
trascorsi. Il ciclo di 4 anni è misurato da qui (indicato con «H»).</td></tr>
<tr><td>Fase del ciclo</td><td>Classificazione in base ai mesi dall'halving: <b>Rialzo post-halving</b>,
<b>Finestra di picco</b> (intorno al mese del picco), <b>Mercato ribassista</b>, <b>Finestra di
minimo</b>, <b>Accumulo</b> (dopo il minimo, prima dell'halving), <b>Pre-halving</b>. Con i valori
predefiniti: picco H+18 mesi, minimo H+30, accumulo H+30→H+48.</td></tr>
<tr><td>Minimo stimato (H+offset)</td><td>Data del minimo attesa: ultimo halving + mesi del documento.</td></tr>
<tr><td>Finestra di minimo</td><td>Intervallo in cui il documento prevede di concentrare gli acquisti
(dal documento, altrimenti minimo stimato ±3 mesi).</td></tr>
<tr><td>Minimo da massimo + 12/13 mesi</td><td>Stima alternativa del minimo: data del massimo di ciclo più i mesi
medi osservati nei cicli passati.</td></tr>
<tr><td>Massimo di ciclo</td><td>Massimo storico del ciclo corrente e <b>drawdown</b> (calo percentuale
del prezzo attuale rispetto ad esso).</td></tr>
<tr><td>Fair value power law</td><td>Valore «teorico» del modello a legge di potenza alla data odierna e
distanza percentuale del prezzo (negativa = sotto).</td></tr>
<tr><td>Floor power law</td><td>Banda inferiore del modello (di norma circa il 42% del fair value) e
distanza del prezzo. Non è un supporto garantito.</td></tr>
<tr><td>Prossimo halving</td><td>Data (stimata) del prossimo dimezzamento, base del piano di uscita.</td></tr>
</table>
<h3>6.3 Ripartizione del capitale</h3>
<p>Divide il capitale in: <b>finestra di minimo</b> (ladder + drip + riserva), <b>DCA esteso</b> e
<b>non allocato</b>. In fase di rialzo/picco tutto il capitale è «non allocato» (nessun acquisto);
la quota «finestra di minimo» è zero se la finestra è chiusa o se sei già in fase di accumulo.</p>
<h3>6.4 Finestra di minimo: ladder, drip e riserva</h3>
<p>Il capitale della finestra è diviso in tre flussi (di norma 50% ladder, 30% drip, 20% riserva).</p>
<ul>
<li><b>Ladder (scala di acquisto).</b> Zone di prezzo decrescenti, ciascuna con una percentuale del
capitale della finestra. Tabella: <i>#</i> gradino; <i>Zona</i> intervallo di prezzo (l'ultima è
«&lt; X», senza limite inferiore); <i>% capitale</i> (con «+ riserva flush» sull'ultimo gradino);
<i>Importo</i> nella tua valuta; <i>BTC stimati</i> se acquistati a metà zona; <i>Scatta a ≤</i> livello di
chiusura giornaliera che attiva l'acquisto; <i>Stato</i>: «IN ZONA ora», «sotto la zona
(acquistabile)» oppure «in attesa (x% dal prezzo)».
Regola chiave: un gradino scatta con una <b>chiusura giornaliera</b> sotto il minimo di chiusura del
ciclo, non con un picco intraday. Non si compra sui rally.</li>
<li><b>Drip (acquisto giornaliero).</b> Una piccola percentuale del capitale (di norma 1% al giorno,
0,5% se «lento») acquistata ogni giorno finché il prezzo è <b>sotto il floor</b> della power law.
Il piano indica importo giornaliero, budget totale, durata in giorni e stato (ATTIVO / in pausa).</li>
<li><b>Riserva.</b> Parte tenuta come munizioni: una porzione (di norma il 10% del capitale della
finestra) è destinata a un «<b>flush</b>» violento, cioè all'ultimo gradino; il resto è
<b>backstop</b>.</li>
<li><b>Anti-miss.</b> Se il mercato non ha offerto le zone attese, dalle ultime 4 settimane della
finestra il capitale non investito va distribuito in rate settimanali (almeno una piccola
percentuale, di norma 3%) entro la fine della finestra, per non restare fuori dal mercato.</li>
</ul>
<h3>6.5 DCA esteso front-loaded</h3>
<p>Il capitale non destinato alla finestra viene investito con un <b>DCA</b> (acquisto periodico)
mensile <b>front-loaded</b>: rate più alte all'inizio, decrescenti. Con i valori predefiniti: 40% nei
mesi 1–3, 30% nei mesi 4–6, 20% nei mesi 7–9, 10% nei mesi 10–12. Parte da H+30 mesi o da oggi se
già oltre.</p>
<table>
<tr><th>Voce</th><th>Significato</th></tr>
<tr><td>Rata base</td><td>Importo mensile secondo il front-load.</td></tr>
<tr><td>Rata max con boost</td><td>Rata base aumentata del tetto massimo dei boost (di norma +50%).</td></tr>
<tr><td>Boost</td><td>Aumenti della rata quando le condizioni sono attive: drawdown dal massimo a 200 giorni
(≥20%), Fear &amp; Greed sotto 25, VIX sopra 25: ciascuno +25%, con un tetto mensile totale (+50%). I
boost non aggiungono capitale: <b>anticipano le rate finali</b> (il piano si accorcia).</td></tr>
<tr><td>Attivo ora</td><td>SÌ / no / n/d (indicatore mancante).</td></tr>
<tr><td>Kill-switch</td><td>Se il prezzo supera la MA200 di oltre il 40% (valore del documento) i boost sono
sospesi: il mercato è considerato surriscaldato.</td></tr>
</table>
<h3>6.6 Cosa comprare</h3>
<p>Composizione degli acquisti: nei primi mesi quasi solo BTC (con ETH fino al limite del profilo), poi
eventuali altcoin «top-N» solo con trend settimanale di BTC al rialzo; da evitare le classifiche
51–100. Nessuna leva finanziaria.</p>
<h3>6.7 Piano di uscita (prossimo ciclo)</h3>
<p>Vendite scalari programmate rispetto al <b>prossimo</b> halving (di norma H+12, H+15, H+18 mesi, 25%
della posizione ciascuna), con la <b>quota che non si vende mai</b> («moon bag», di norma 25%). Le note
indicano: finestra di picco attesa (halving + 500–550 giorni), conferma secondaria con RSI settimanale
sopra una soglia (di norma 80), vendita senza esitazioni se compaiono 3+ segnali di euforia nella
finestra, e prese di profitto parziali al raggiungimento di un nuovo massimo storico.</p>
<h3>6.8 Livelli che decidono lo scenario</h3>
<p><b>Livello di invalidazione rialzista</b>: una chiusura sopra indica che il ribasso è finito (si passa a
DCA semplice). <b>Livello ribassista</b>: una chiusura sotto indica la gamba finale del ribasso (si
usa la ladder). Il piano mostra la distanza percentuale dal prezzo o «ROTTO».</p>
<h3>6.9 Scenari e stime del minimo per fonte</h3>
<ul>
<li><b>Scenario minimo</b>: ipotesi di minimo (prezzo e drawdown dal massimo): conservativo, base,
aggressivo.</li>
<li><b>Picco implicito</b>: dal minimo ipotizzato, il picco corrispondente ai guadagni storici
attesi (es. +200% … +400%).</li>
<li><b>Obiettivo di picco dichiarato</b>: se presente nel documento.</li>
<li><b>Stime del minimo per fonte</b>: ogni documento con il proprio intervallo di prezzo; serve a
vedere quanto le fonti divergono.</li>
</ul>
<h3>6.10 Avvertenze (partner critico)</h3>
<p>Elenco di rischi generato dai dati. Non ignorarlo:</p>
<ul>
<li><b>Fonte unica:</b> tutti i documenti dello stesso autore → rischio di bias di conferma.</li>
<li><b>Contenuti promozionali</b> e track record auto-dichiarati.</li>
<li><b>Stime divergenti</b> del minimo; <b>incoerenza tra modelli</b> (es. range di minimo che implica la
rottura del floor).</li>
<li><b>Campione ridotto:</b> il «ciclo di 4 anni» poggia su 4 osservazioni; ETF e istituzionali possono
cambiarne tempi e ampiezza.</li>
<li><b>Date troppo note:</b> se tutti conoscono la finestra, può essere anticipata (front-running).</li>
<li><b>Il floor non è garantito:</b> è stato rotto in passato; viene mostrato il prezzo equivalente.</li>
<li><b>Stress test:</b> prezzo medio stimato della ladder e perdita se BTC scendesse al floor rotto.</li>
<li><b>Rendimenti decrescenti</b> ciclo dopo ciclo e <b>dati di mercato incompleti</b>.</li>
</ul>
<h3>6.11 Fonti e parametri usati</h3>
<p>Elenco dei documenti (titolo, data, fonte) e tabella di ogni parametro effettivamente usato, con
valore e documento di origine («predefinito» se non presente nei documenti). Serve per
riprodurre e verificare ogni numero del piano.</p>

<h2>7. Scheda Grafico</h2>
<h3>7.1 Cosa mostra</h3>
<table>
<tr><th>Elemento</th><th>Significato</th></tr>
<tr><td>Linea nera</td><td>Chiusure giornaliere del prezzo BTC (ultimi 365 giorni).</td></tr>
<tr><td>Linea arancione</td><td>Prezzo corrente (si aggiorna ogni 60 secondi, solo con la scheda visibile).</td></tr>
<tr><td>Fasce verdi «Ladder n»</td><td>Zone di acquisto della ladder, con intervallo e percentuale del capitale.</td></tr>
<tr><td>Curva grigia / verde tratteggiate</td><td>Fair value e floor della power law, proiettati nel
futuro. Oltre l'orizzonte dei dati sono estrapolazioni del modello.</td></tr>
<tr><td>Linea blu «MA200»</td><td>Media mobile a 200 giorni (se inserita nel piano).</td></tr>
<tr><td>Linee rosse tratteggiate di livello</td><td>Livelli di invalidazione rialzista/ribassista.</td></tr>
<tr><td>Fascia arancione «Finestra di minimo» e linea «Minimo stimato»</td><td>Periodo e data attesi del
minimo di ciclo.</td></tr>
<tr><td>Barra sopra il grafico</td><td>Prezzo, gradino di ladder più vicino e distanza, rally dal minimo del
ciclo confrontato con la mediana dei rally falliti (+35%, 15 casi: solo contesto), stato
dell'aggiornamento.</td></tr>
<tr><td>Riga in basso</td><td>Fonti usate e avviso «stime di terzi, non previsioni».</td></tr>
</table>
<h3>7.2 Controlli</h3>
<ul>
<li><b>Scala logaritmica:</b> in scala log distanze uguali rappresentano variazioni percentuali uguali;
è la scala adatta per confrontare cicli diversi. Gli assi mostrano potenze di 10 (es. 9·10⁴ = 90.000).</li>
<li><b>Mostra uscite:</b> estende l'asse fino alle vendite programmate. Mostra le linee verticali
«Vendi 25% · resta 75%», la <b>finestra di picco</b> e l'<b>obiettivo di picco</b> dichiarato. Le uscite sono
a data, non a prezzo: i prezzi sono solo stime (obiettivo e scenari).</li>
<li><b>Click sinistro</b> su un punto: traccia le linee del prezzo e della data in quel punto, con
etichetta (data, prezzo, scarto dal prezzo attuale). <b>Click destro</b>: le rimuove.</li>
<li><b>Rotella / trascinamento:</b> zoom e spostamento. <b>Reimposta vista</b> ripristina
l'inquadratura iniziale.</li>
<li><b>Aggiorna storico:</b> riscarica i 365 giorni di chiusure.</li>
<li><b>Esporta immagine… / Copia:</b> salva o copia in PNG il grafico con barra di stato e fonti
(senza pulsanti), pronto da condividere. Ingrandisci la finestra per un'immagine più nitida.</li>
</ul>

<h2>8. Menu, lingua, aggiornamenti e dati salvati</h2>
<table>
<tr><th>Menu</th><th>Voci</th></tr>
<tr><td>File</td><td>Importa documenti… (Ctrl+O), Importa cartella…, Esporta piano (HTML/Markdown), Esci.</td></tr>
<tr><td>Dati</td><td>Aggiorna dati di mercato (F5), Genera piano (Ctrl+G), Rianalizza tutti i documenti,
Rimuovi documento selezionato, Apri cartella dati.</td></tr>
<tr><td>Strumenti</td><td>Documenti e parametri…, Lingua (Italiano / English: si applica al prossimo
avvio).</td></tr>
<tr><td>Aiuto</td><td>Guida (finestra con indice e ricerca, F1), Guida (PDF) (questo documento), Controlla aggiornamenti, Informazioni (autore e versione).</td></tr>
</table>
<ul>
<li><b>Lingua:</b> al primo avvio segue la lingua del sistema (italiano se it, altrimenti inglese). Il
piano, l'esportazione e questa guida seguono la lingua scelta.</li>
<li><b>Aggiornamenti:</b> all'avvio il programma controlla in background le release su GitHub e, se
disponibile una versione più recente, ti chiede se scaricarla e installarla. La verifica manuale è
in <i>Aiuto → Controlla aggiornamenti</i>.</li>
<li><b>Dati salvati:</b> la knowledge base (documenti e parametri) e le impostazioni (capitale, valuta,
profilo, indicatori, preferenze del grafico) restano sul tuo computer. <i>Dati → Apri cartella dati</i>
apre la cartella; non viene inviato nulla a server esterni, salvo le richieste a CoinGecko,
alternative.me e GitHub.</li>
</ul>

<h2>9. Glossario</h2>
<table>
<tr><th>Termine</th><th>Significato</th></tr>
<tr><td>Halving (H)</td><td>Dimezzamento della ricompensa dei blocchi, ogni 210.000 blocchi (circa 4 anni).
Date: 2012, 2016, 2020, 2024; prossimo stimato aprile 2028. «H+18» = 18 mesi dopo l'halving.</td></tr>
<tr><td>Ciclo di 4 anni</td><td>Schema osservato di rialzo, picco, ribasso e minimo legato agli halving. Basato
su 4 soli cicli.</td></tr>
<tr><td>Power law</td><td>Modello che lega il prezzo ai giorni dal blocco genesi (3 gennaio 2009):
prezzo = A × giorni^B (esponente standard 5,82).</td></tr>
<tr><td>Fair value / floor</td><td>Valore centrale del modello / banda inferiore (di norma ~42% del fair value).</td></tr>
<tr><td>Drawdown</td><td>Calo percentuale dal massimo precedente.</td></tr>
<tr><td>DCA</td><td>Dollar-cost averaging: acquisti periodici di importo prefissato.</td></tr>
<tr><td>Front-loaded</td><td>DCA con rate più alte all'inizio del periodo.</td></tr>
<tr><td>Ladder</td><td>Scala di ordini a livelli di prezzo decrescenti.</td></tr>
<tr><td>Drip</td><td>Acquisto giornaliero di piccola entità mentre il prezzo è sotto il floor.</td></tr>
<tr><td>Flush</td><td>Crollo violento e rapido dei prezzi; la riserva ne prevede lo sfruttamento.</td></tr>
<tr><td>Backstop</td><td>Quota di riserva non destinata al flush, usata come rete di sicurezza.</td></tr>
<tr><td>Anti-miss</td><td>Regola che impone di investire il residuo in rate settimanali verso la fine della
finestra.</td></tr>
<tr><td>Boost</td><td>Aumento temporaneo della rata DCA quando le condizioni di stress sono attive.</td></tr>
<tr><td>Kill-switch</td><td>Condizione che sospende i boost (prezzo molto sopra la MA200).</td></tr>
<tr><td>MA200</td><td>Media mobile semplice a 200 giorni.</td></tr>
<tr><td>Fear &amp; Greed</td><td>Indice di sentiment di mercato da 0 (paura estrema) a 100 (avidità estrema).</td></tr>
<tr><td>VIX</td><td>Indice di volatilità implicita dell'S&amp;P 500, indicatore di stress macro.</td></tr>
<tr><td>RSI settimanale</td><td>Indicatore di momentum a 14 periodi su candele settimanali; sopra 80 =
surriscaldamento.</td></tr>
<tr><td>Moon bag</td><td>Quota della posizione che non si vende mai.</td></tr>
<tr><td>Invalidazione</td><td>Livello oltre il quale lo scenario base non è più valido.</td></tr>
<tr><td>Front-running</td><td>Anticipare le mosse del mercato su date/livelli molto noti.</td></tr>
<tr><td>Chiusura giornaliera</td><td>Prezzo di chiusura della candela giornaliera (non il minimo intraday).</td></tr>
<tr><td>Knowledge base</td><td>Archivio locale dei documenti importati e dei parametri estratti.</td></tr>
<tr><td>Insight</td><td>Singola informazione estratta da un documento, con pagina ed evidenza.</td></tr>
</table>

<h2>10. Limiti, avvertenze e risoluzione dei problemi</h2>
<h3>Limiti del metodo</h3>
<ul>
<li>L'estrazione usa regole su testo in inglese e sul formato dei documenti noti; altri documenti
potrebbero essere letti solo in parte.</li>
<li>Il modello presuppone che il futuro assomigli a 4 cicli passati. I mercati cambiano.</li>
<li>I dati di mercato sono gratuiti e possono ritardare o essere limitati nelle richieste.</li>
<li>Il piano non conosce la tua situazione fiscale, il tuo orizzonte o la tua tolleranza al rischio.</li>
</ul>
<h3>Problemi frequenti</h3>
<table>
<tr><th>Problema</th><th>Cosa fare</th></tr>
<tr><td>«Genera piano» dice che capitale e prezzo devono essere maggiori di zero</td><td>Compila Capitale e Prezzo
BTC (o premi «Aggiorna dati di mercato»).</td></tr>
<tr><td>Nessun testo estraibile dal PDF</td><td>Il PDF è un'immagine: convertilo con OCR o usa una versione testuale.</td></tr>
<tr><td>Download dati di mercato non riuscito</td><td>Controlla la connessione; il servizio gratuito può limitare le
richieste: riprova dopo un minuto, oppure inserisci i valori a mano.</td></tr>
<tr><td>Un parametro mostra il valore predefinito</td><td>Il documento non lo contiene o non è stato riconosciuto:
controlla l'evidenza in <i>Strumenti → Documenti e parametri…</i>.</td></tr>
<tr><td>Dopo un aggiornamento i dati sembrano vecchi</td><td>Usa <i>Dati → Rianalizza tutti i documenti</i>.</td></tr>
<tr><td>Il grafico non si aggiorna</td><td>Il polling avviene solo con la scheda visibile; premi «Aggiorna storico».</td></tr>
<tr><td>La lingua non cambia</td><td>La lingua si applica al riavvio dell'applicazione.</td></tr>
</table>
<p class="note"><b>Ricorda:</b> strumento educativo, non consulenza finanziaria. Nessun modello elimina il
rischio di perdita del capitale.</p>
"""
