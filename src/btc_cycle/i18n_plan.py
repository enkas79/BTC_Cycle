"""Traduzioni inglesi del piano, delle fasi del ciclo e delle etichette dei parametri estratti."""

EN_PLAN = {
    # fasi del ciclo
    "Rialzo post-halving": "Post-halving rally",
    "Fase storicamente rialzista: mantenere, niente nuovi acquisti aggressivi.":
        "Historically bullish phase: hold, no aggressive new purchases.",
    "Finestra di picco": "Peak window",
    "Zona temporale dei massimi storici di ciclo: applicare il piano di uscita.":
        "Time zone of the cycle's all-time highs: apply the exit plan.",
    "Mercato ribassista": "Bear market",
    "Distribuzione e calo: preservare il capitale, preparare i livelli di acquisto.":
        "Distribution and decline: preserve capital, prepare the buy levels.",
    "Zona temporale dei minimi di ciclo: ladder + drip + riserva.":
        "Time zone of the cycle lows: ladder + drip + reserve.",
    "Accumulo": "Accumulation",
    "Dopo il minimo, prima dell'halving: DCA front-loaded con boost.":
        "After the low, before the halving: front-loaded DCA with boosts.",
    "Pre-halving": "Pre-halving",
    "Ciclo maturo: mantenere, prepararsi al rialzo post-halving.":
        "Mature cycle: hold, get ready for the post-halving rally.",
    # report: titoli e tabelle
    "Piano di investimento Bitcoin": "Bitcoin investment plan",
    "Generato il {d} · profilo {p} · non è consulenza finanziaria":
        "Generated on {d} · profile {p} · not financial advice",
    "Cosa fare adesso": "What to do now", "Nessuna azione.": "No action.",
    "Situazione di mercato e ciclo": "Market and cycle situation", "Voce": "Item",
    "Data analisi": "Analysis date", "Prezzo BTC": "BTC price", "Ultimo halving": "Last halving",
    "{d} ({days} giorni, {m:.1f} mesi)": "{d} ({days} days, {m:.1f} months)",
    "Fase del ciclo": "Cycle phase", "Minimo stimato (H+offset)": "Estimated low (H+offset)",
    "Minimo da massimo+12/13 mesi": "Low from high + 12/13 months",
    "Massimo di ciclo": "Cycle high", "{p} ({d}) — drawdown {dd}": "{p} ({d}) — drawdown {dd}",
    "{v} (prezzo {p})": "{v} (price {p})", "Prossimo halving": "Next halving",
    "Ripartizione del capitale": "Capital allocation", "Quota": "Share", "Importo": "Amount",
    "Capitale totale": "Total capital", "Capitale 'finestra di minimo' ({p:.0f}%)": "'Bottom window' capital ({p:.0f}%)",
    "Capitale DCA esteso": "Extended DCA capital", "Non allocato": "Unallocated",
    "Zone riancorate al floor attuale (fattore {f:.3f}).": "Zones re-anchored to the current floor (factor {f:.3f}).",
    "Zone come da documento.": "Zones as in the document.",
    "Finestra di minimo: ladder, drip e riserva": "Bottom window: ladder, drip and reserve",
    "Regola: un gradino scatta solo con una chiusura giornaliera sotto il minimo di chiusura del ciclo (non con uno spike intraday). ":
        "Rule: a rung triggers only on a daily close below the cycle's closing low (not on an intraday spike). ",
    "Zona": "Zone", "% capitale": "% of capital", "BTC stimati": "Est. BTC", "Scatta a ≤": "Triggers at ≤",
    "Stato": "Status", " + riserva flush": " + flush reserve",
    "Drip: {pct}% al giorno = {daily:,.0f} {cur} finché il prezzo è sotto il floor ({fl}); budget {tot:,.0f} {cur} ≈ {days} giorni. Stato: {st}.":
        "Drip: {pct}% per day = {daily:,.0f} {cur} while the price is below the floor ({fl}); budget {tot:,.0f} {cur} ≈ {days} days. Status: {st}.",
    "ATTIVO": "ACTIVE", "in pausa": "paused",
    "Riserva: {tot:,.0f} {cur}, di cui {fl:,.0f} per un flush violento (ultimo gradino) e {bk:,.0f} di backstop.":
        "Reserve: {tot:,.0f} {cur}, of which {fl:,.0f} for a violent flush (last rung) and {bk:,.0f} as backstop.",
    "Anti-miss: dal {d}, se sei sotto-investito, distribuisci il residuo in rate settimanali (≥ {w:,.0f} {cur}/sett.) entro {e}.":
        "Anti-miss: from {d}, if you are under-invested, spread the remainder in weekly installments (≥ {w:,.0f} {cur}/week) by {e}.",
    "Mai comprare su candele verdi/rally; se il prezzo rompe al rialzo prima delle zone profonde, passa a DCA semplice.":
        "Never buy on green candles/rallies; if the price breaks upward before the deep zones, switch to plain DCA.",
    "DCA esteso front-loaded": "Extended front-loaded DCA", "DCA esteso": "Extended DCA",
    "Inizio: {d}. Rate mensili decrescenti (front-load).": "Start: {d}. Decreasing monthly installments (front-load).",
    "Mese": "Month", "% capitale DCA": "% of DCA capital", "Rata base": "Base installment",
    "Rata max con boost": "Max installment with boost", "Boost": "Boost", "Incremento": "Increase",
    "Attivo ora": "Active now", "SÌ": "YES", "no": "no",
    "n/d (serve MA200)": "n/a (needs MA200)", "ATTIVO: boost sospesi": "ACTIVE: boosts suspended",
    "non attivo": "not active",
    "Boost totale attuale: +{t:.0f}% (tetto +{c:.0f}%).": "Current total boost: +{t:.0f}% (cap +{c:.0f}%).",
    "Kill-switch (prezzo > MA200 +{p:.0f}%): {k}.": "Kill-switch (price > MA200 +{p:.0f}%): {k}.",
    "Cosa comprare": "What to buy", "Piano di uscita (prossimo ciclo)": "Exit plan (next cycle)",
    "mesi": "months", "Offset": "Offset", "Vendi (% posizione)": "Sell (% of position)", "Residuo": "Remaining",
    "Livelli che decidono lo scenario": "Levels that decide the scenario", "Livello": "Level",
    "Prezzo": "Price", "Tipo": "Type", "rialzo": "upside", "ribasso": "downside",
    "Scenari e stime del minimo per fonte": "Scenarios and low estimates by source",
    "Scenario minimo": "Low scenario", "Drawdown": "Drawdown", "Da minimo": "From low",
    "Guadagno": "Gain", "Picco implicito": "Implied peak", "Fonte": "Source", "Stima": "Estimate",
    "Minimo": "Low", "Massimo": "High",
    "Obiettivo di picco dichiarato: {p}.": "Stated peak target: {p}.",
    "Avvertenze (partner critico)": "Warnings (critical partner)",
    "Fonti e parametri usati": "Sources and parameters used",
    "Nessun documento: uso solo parametri predefiniti.": "No documents: using default parameters only.",
    "Parametro": "Parameter", "Valore": "Value",
    # planner
    "Fase di rialzo/picco: i documenti non prevedono nuovi acquisti ora. Il capitale resta non allocato fino alla prossima finestra di minimo.":
        "Rally/peak phase: the documents do not foresee new purchases now. Capital stays unallocated until the next bottom window.",
    "IN ZONA ora": "IN ZONE now", "sotto la zona (acquistabile)": "below the zone (buyable)",
    "in attesa ({d:+.1f}% dal prezzo)": "waiting ({d:+.1f}% from price)",
    "La finestra di accumulo primaria (H+48) è già chiusa.": "The primary accumulation window (H+48) is already closed.",
    "I boost si finanziano anticipando le rate finali (il piano si accorcia), non aggiungendo capitale nuovo.":
        "Boosts are funded by pulling forward the final installments (the plan gets shorter), not by adding new capital.",
    "BTC ≥{t}% sotto il massimo a 200 giorni": "BTC ≥{t}% below the 200-day high",
    "Fear & Greed sotto {t}": "Fear & Greed below {t}",
    "VIX sopra {t} (o picco di volatilità crypto)": "VIX above {t} (or crypto volatility spike)",
    "Primi {m} mesi: {btc:.0f}% BTC": "First {m} months: {btc:.0f}% BTC",
    ", fino a {eth:.0f}% ETH.": ", up to {eth:.0f}% ETH.", " (profilo: niente ETH).": " (profile: no ETH).",
    "Mesi {a}–{b}: fino a {mx:.0f}% in altcoin top-{top}, solo con trend settimanale di BTC al rialzo. Evitare ranking 51–100 (nei dati dei documenti: rendimenti negativi e molti fallimenti).":
        "Months {a}–{b}: up to {mx:.0f}% in top-{top} altcoins, only with BTC's weekly trend up. Avoid ranks 51–100 (in the documents' data: negative returns and many failures).",
    "Profilo prudente: 100% BTC, nessuna altcoin.": "Prudent profile: 100% BTC, no altcoins.",
    "Nessuna leva finanziaria.": "No leverage.",
    "Finestra di picco attesa: {a:%b %Y} – {b:%b %Y} (halving {h:%b %Y} + {d0}–{d1} giorni).":
        "Expected peak window: {a:%b %Y} – {b:%b %Y} (halving {h:%b %Y} + {d0}–{d1} days).",
    "Quota da non vendere mai (moon bag): {moon}%.": "Share never to sell (moon bag): {moon}%.",
    "Conferma secondaria: RSI settimanale sopra {rsi}.": "Secondary confirmation: weekly RSI above {rsi}.",
    "Vendi senza esitare se compaiono {n}+ segnali di euforia nella finestra temporale.":
        "Sell without hesitation if {n}+ euphoria signals appear within the time window.",
    "Nuovo massimo storico → inizia subito le prese di profitto parziali.":
        "New all-time high → start partial profit-taking right away.",
    "ROTTO: trend ribassista finito → DCA semplice": "BROKEN: bear trend over → plain DCA",
    "ROTTO: gamba finale ribassista → ladder": "BROKEN: final bearish leg → ladder",
    "{d:+.1f}% dal prezzo": "{d:+.1f}% from price",
    "Conservativo": "Conservative", "Base": "Base", "Aggressivo": "Aggressive",
    "Nessun acquisto: fase di rialzo/picco. Segui il piano di uscita.": "No purchases: rally/peak phase. Follow the exit plan.",
    "Livello rialzista rotto: sospendi la ladder e passa a DCA semplice (regola 'shift to plain DCA').":
        "Upside level broken: suspend the ladder and switch to plain DCA ('shift to plain DCA' rule).",
    "Ladder gradino {n}: acquista {amt:,.0f} {cur} alla prossima chiusura giornaliera ≤ {trg} (nuovo minimo).":
        "Ladder rung {n}: buy {amt:,.0f} {cur} at the next daily close ≤ {trg} (new low).",
    "Drip ATTIVO (prezzo sotto il floor {fl}): {amt:,.0f} {cur} al giorno.":
        "Drip ACTIVE (price below the floor {fl}): {amt:,.0f} {cur} per day.",
    "Drip in pausa: il prezzo è sopra il floor {fl}.": "Drip paused: the price is above the floor {fl}.",
    "Nessun gradino attivo: il primo scatta a chiusura ≤ {trg}. Non inseguire i rally.":
        "No active rung: the first triggers on a close ≤ {trg}. Do not chase rallies.",
    "Anti-miss ATTIVO: se sei investito meno del previsto, distribuisci il residuo del capitale 'minimo' in ~{w} rate settimanali entro {d}.":
        "Anti-miss ACTIVE: if you are invested less than planned, spread the remainder of the 'bottom' capital over ~{w} weekly installments by {d}.",
    "Promemoria anti-miss: dal {d} valuta il capitale non investito.": "Anti-miss reminder: from {d} review the uninvested capital.",
    "DCA: prima rata {amt:,.0f} {cur} il {d}": "DCA: first installment {amt:,.0f} {cur} on {d}",
    " (boost +{b:.0f}%)": " (boost +{b:.0f}%)", ", poi mensile secondo il calendario.": ", then monthly following the schedule.",
    "Fase ribassista prima della finestra: preserva il capitale e prepara gli ordini.":
        "Bear phase before the window: preserve capital and prepare the orders.",
    "Tutti i {n} documenti provengono dalla stessa fonte ({src}): nessuna verifica indipendente, rischio di bias di conferma. Aggiungi analisi di autori diversi, idealmente con tesi contrarie.":
        "All {n} documents come from the same source ({src}): no independent verification, risk of confirmation bias. Add analyses by different authors, ideally with opposing views.",
    "Documenti con finalità promozionale (portano a canali a pagamento): {docs}. I track record citati sono auto-dichiarati.":
        "Documents with a promotional purpose (they lead to paid channels): {docs}. The track records cited are self-reported.",
    "Le stime del minimo divergono: da {lo} ({lo_doc}) a {hi} ({hi_doc}). Il piano non dipende da un singolo numero, ma la dispersione indica incertezza reale.":
        "Low estimates diverge: from {lo} ({lo_doc}) to {hi} ({hi_doc}). The plan does not depend on a single number, but the spread signals real uncertainty.",
    "Incoerenza tra modelli: il range di minimo {lo}–{hi} implica una rottura del floor power law ({fl}) di oltre {p:.0f}%. Uno dei due modelli è sbagliato.":
        "Model inconsistency: the low range {lo}–{hi} implies a break of the power-law floor ({fl}) of more than {p:.0f}%. One of the two models is wrong.",
    "Il 'ciclo di 4 anni' si basa su 4 osservazioni (2012, 2016, 2020, 2024): un campione minimo. ETF e istituzionali possono alterarne tempi e ampiezza.":
        "The '4-year cycle' rests on 4 observations (2012, 2016, 2020, 2024): a minimal sample. ETFs and institutions may alter its timing and size.",
    "La data del minimo attesa (ott-nov) è la più osservata dal mercato: lo stesso documento avverte che può essere anticipata dagli operatori (front-running).":
        "The expected low date (Oct–Nov) is the one the market watches most: the same document warns that traders may front-run it.",
    "Il floor power law non è un supporto garantito: in passato è stato rotto fino al {p:.0f}%. Oggi equivarrebbe a circa {worst}.":
        "The power-law floor is not guaranteed support: in the past it was broken by up to {p:.0f}%. Today that would be about {worst}.",
    "Stress test: prezzo medio stimato della ladder {avg}; con BTC a {worst} la posizione segnerebbe {loss:.0f}%. Assicurati di poterlo sostenere per anni.":
        "Stress test: estimated average ladder price {avg}; with BTC at {worst} the position would show {loss:.0f}%. Make sure you can hold through that for years.",
    "Rendimenti decrescenti ciclo dopo ciclo ({h}): proiettare il passato sul futuro è un'ipotesi, non un fatto.":
        "Diminishing returns cycle after cycle ({h}): projecting the past onto the future is an assumption, not a fact.",
    "Dati di mercato incompleti: alcuni boost/kill-switch non sono valutabili.":
        "Incomplete market data: some boosts/kill-switch cannot be evaluated.",
    "Power law non calibrata dai documenti: uso parametri standard (Santostasi).":
        "Power law not calibrated from the documents: using standard parameters (Santostasi).",
    "Il capitale del piano deve essere denaro che puoi tenere fermo 4+ anni, separato dal fondo di emergenza. Questo software non è consulenza finanziaria.":
        "The plan's capital must be money you can leave untouched for 4+ years, separate from your emergency fund. This software is not financial advice.",
    "({d:+.1f}% dal prezzo attuale)": "({d:+.1f}% vs current price)",
    # flag e fonti
    "promozionale (funnel verso contenuti a pagamento)": "promotional (funnel to paid content)",
    "disclaimer: non è consulenza finanziaria": "disclaimer: not financial advice",
    "campioni statistici ridotti dichiarati": "small statistical samples declared",
    "sconosciuta": "unknown",
    # etichette dei parametri
    "Picco (mesi post-halving)": "Peak (months after halving)", "Minimo (mesi post-halving)": "Low (months after halving)",
    "Accumulo (mesi post-halving)": "Accumulation (months after halving)",
    "Finestra di accumulo": "Accumulation window", "Massimo di ciclo ": "Cycle high ",
    "Mesi massimo→minimo": "Months high→low", "Ancora fair value power law": "Power-law fair value anchor",
    "Floor power law": "Power law floor", "Zone ladder": "Ladder zones", "Flussi ladder/drip/riserva": "Ladder/drip/reserve streams",
    "Drip giornaliero %": "Daily drip %", "DCA front-loaded": "Front-loaded DCA", "Vendite programmate": "Scheduled sales",
    "Livello rialzista": "Upside level", "Livello ribassista": "Downside level",
    "Accumulo primario (mesi dopo halving)": "Primary accumulation (months after halving)",
    "Anti-miss: % a settimana": "Anti-miss: % per week", "Boost massimo mensile (%)": "Maximum monthly boost (%)",
    "DCA front-loaded (% per blocco di mesi)": "Front-loaded DCA (% per block of months)",
    "Drawdown storici dei bear (%)": "Historical bear-market drawdowns (%)",
    "Drip giornaliero (% del capitale)": "Daily drip (% of capital)", "Drip giornaliero lento (%)": "Slow daily drip (%)",
    "Durata DCA (mesi)": "DCA duration (months)", "Esponente power law": "Power-law exponent",
    "Fear & Greed sostenuto sotto": "Fear & Greed sustained below", "Giorni halving → picco": "Days halving → peak",
    "Guadagno atteso minimo→picco successivo (%)": "Expected gain low→next peak (%)",
    "Kill-switch boost: % sopra MA200": "Boost kill-switch: % above MA200",
    "Mesi dal massimo al minimo (cicli passati)": "Months from high to low (past cycles)",
    "Obiettivo di picco": "Peak target", "Quota da tenere per sempre (%)": "Share to hold forever (%)",
    "RSI settimanale sopra (top)": "Weekly RSI above (top)", "RSI settimanale sotto (bottom)": "Weekly RSI below (bottom)",
    "Rally dal minimo recente": "Rally from the recent low",
    "Rendimenti minimo→picco per ciclo (%)": "Low→peak returns per cycle (%)",
    "Ripartizione flussi (ladder/drip/riserva %)": "Stream split (ladder/drip/reserve %)",
    "Riserva per flush violento (%)": "Reserve for violent flush (%)",
    "Rotture storiche del floor (% sotto)": "Historical floor breaches (% below)",
    "Scenari di minimo (drawdown dal massimo)": "Low scenarios (drawdown from high)",
    "Segnali di bottom minimi in confluenza": "Minimum bottom signals in confluence",
    "Segnali di euforia minimi": "Minimum euphoria signals", "Vendite programmate (mesi dopo halving)": "Scheduled sales (months after halving)",
    "Zone della ladder (% del capitale)": "Ladder zones (% of capital)", "stagionalità": "seasonality",
    "Vendi {pct}% · resta {rem:.0f}%": "Sell {pct}% · {rem:.0f}% left",
    "Obiettivo di picco · {p}": "Peak target · {p}",
    "Mostra uscite": "Show exits", "Esporta immagine…": "Export image…", "Copia": "Copy",
    "Grafico copiato negli appunti.": "Chart copied to the clipboard.",
    "Guida salvata in:\n{path}": "Guide saved to:\n{path}",
    "Cerca nella guida…": "Search the guide…", "Apri PDF": "Open PDF", "Guida (PDF)": "Guide (PDF)",
    "prudente": "prudent", "bilanciato": "balanced", "aggressivo": "aggressive",
    "Allocazione iniziale": "Initial allocation", "Boost se -X% dal massimo 200gg": "Boost if -X% from 200-day high",
    "Boost se Fear & Greed sotto X": "Boost if Fear & Greed below X", "Boost se VIX sopra X": "Boost if VIX above X",
    "Diversificazione in altcoin": "Altcoin diversification",
    "Dopo rally fallito: calo mediano (%)": "After failed rally: median drop (%)",
    "Floor (banda inferiore) power law": "Power-law floor (lower band)",
    "Inizio DCA (mesi dopo halving)": "DCA start (months after halving)",
    "Livello citato (obiettivo)": "Cited level (target)", "Livello citato (supporto)": "Cited level (support)",
    "Livello rialzista (chiusura sopra = trend cambia)": "Upside level (close above = trend changes)",
    "Livello ribassista (chiusura sotto = gamba finale)": "Downside level (close below = final leg)",
    "Mai comprare nei rally (no FOMO)": "Never buy rallies (no FOMO)",
    "Minimo stimato (mesi dopo halving)": "Estimated low (months after halving)",
    "Nessuna leva": "No leverage", "Nuovo minimo = chiusura giornaliera, non spike": "New low = daily close, not a spike",
    "Picco stimato (mesi dopo halving)": "Estimated peak (months after halving)",
    "Prezzo vs fair value power law": "Price vs power-law fair value",
    "Pullback mediano anche a bottom confermato (%)": "Median pullback even with confirmed bottom (%)",
    "Rally ribassista fallito: guadagno mediano (%)": "Failed bear rally: median gain (%)",
    "Range del minimo di ciclo": "Cycle low range", "Errore di estrazione": "Extraction error",
    "Se rompe al rialzo prima: passa a DCA semplice": "If it breaks upward first: switch to plain DCA",
}
