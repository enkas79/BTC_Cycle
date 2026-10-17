"""Guide PDF text (English). Placeholders: {app}, {version}."""

GUIDE_EN = """
<h1>{app}</h1>
<p class="sub">Complete guide to using the program and to the meaning of every item — version {version}</p>
<p class="note"><b>Disclaimer.</b> This program is an educational tool. It does not provide financial
advice, does not predict prices and does not guarantee any result. All levels, dates and percentages
come from the documents you import (third-party estimates) and from the market data downloaded:
always verify them with independent sources before deciding. Invest only capital you can leave
untouched for years.</p>

<h2>Contents</h2>
<ol>
<li>What it is for and how it reasons</li>
<li>Quick start in 6 steps</li>
<li>Window overview</li>
<li>Importing and managing documents</li>
<li>Plan tab: the fields to fill in</li>
<li>How to read the generated plan</li>
<li>Chart tab</li>
<li>Menus, language, updates and saved data</li>
<li>Glossary</li>
<li>Limits, warnings and troubleshooting</li>
</ol>

<h2>1. What it is for and how it reasons</h2>
<p>Many analysts publish Bitcoin-cycle strategies as PDFs (timing from the halvings, buy zones,
capital percentages, selling plans). {app} does three things:</p>
<ol>
<li><b>Reads</b> the documents (PDF, TXT, MD) and <b>extracts the numeric parameters</b> with fixed,
transparent rules. Every extracted value keeps the page and the text excerpt it came from.</li>
<li><b>Aggregates</b> the documents: for each parameter the most recent document wins; differing
values from the other documents are flagged as conflicts.</li>
<li><b>Combines</b> the parameters with current price and market indicators and with your capital to
produce an <b>operational plan</b> (what to do today, how much, at which levels and when) and a
<b>chart</b> with price, levels and time windows.</li>
</ol>
<p>The program does not decide for you: it applies the documents' rules mechanically and, on top, it
shows <b>critical warnings</b> (single source, promotional content, diverging estimates, minimal
statistical sample, stress test).</p>
<p><b>If a parameter is not present in the documents</b> the plan uses a default value and says so in
the «Sources and parameters used» section ("default").</p>

<h2>2. Quick start in 6 steps</h2>
<ol>
<li><b>Import the documents</b>: menu <i>File → Import documents…</i> (Ctrl+O), <i>Import
folder…</i>, or drag the files into the window.</li>
<li>(Optional) open <i>Tools → Documents and parameters…</i> to check what was extracted and
whether there are conflicts.</li>
<li>In the <b>Plan</b> tab enter <b>Capital</b> and <b>Currency</b>.</li>
<li>Press <b>Refresh market data</b> (F5): it fills price, exchange rate, 200-day MA, 200-day high,
cycle closing low and Fear &amp; Greed. VIX must be entered by hand (optional).</li>
<li>Choose the <b>Profile</b> and strategy options, then press <b>Generate plan</b> (Ctrl+G).</li>
<li>Read the plan on the right (start with «What to do now» and «Warnings»), open the
<b>Chart</b> tab and, if you want, export the plan (HTML/Markdown) or the chart image.</li>
</ol>

<h2>3. Window overview</h2>
<table>
<tr><th>Element</th><th>Content</th></tr>
<tr><td>Menu bar</td><td><b>File</b> (import, export, quit), <b>Data</b> (market, plan, re-analysis,
removal, data folder), <b>Tools</b> (documents and parameters, language), <b>Help</b> (guide, updates,
about).</td></tr>
<tr><td>Plan tab</td><td>Input fields on the left; the generated plan report on the right.</td></tr>
<tr><td>Chart tab</td><td>BTC price with the strategy's levels, bands and time windows.</td></tr>
<tr><td>Status bar</td><td>Status messages and, on the right, the number of documents and parameters in the
knowledge base.</td></tr>
</table>
<p>Long operations (import, data download, update check) run in the background: the interface stays
usable. On a network error a warning appears, but the application does not freeze.</p>

<h2>4. Importing and managing documents</h2>
<h3>4.1 Formats and import</h3>
<ul>
<li><b>Formats:</b> PDFs with selectable text, TXT, MD. A scanned PDF (images only) cannot be read: an
external OCR is required.</li>
<li><b>How:</b> <i>File → Import documents…</i>, <i>Import folder…</i> (includes subfolders) or drag and
drop into the window.</li>
<li><b>Duplicates:</b> each file has a fingerprint (hash): if you re-import it, it is recognized and
updated, not duplicated. The final message says how many documents are new and how many updated.</li>
</ul>
<h3>4.2 What is extracted</h3>
<p>The rules search the text (in English and in the formats used by the authors) for these groups of
information:</p>
<table>
<tr><th>Group</th><th>Example parameters</th></tr>
<tr><td>Cycle</td><td>Months from halving to peak and to low, accumulation window, days halving→peak, cycle
high (price and date), months from high to low in past cycles, historical drawdowns and returns, low
scenarios, next halving date.</td></tr>
<tr><td>Power law</td><td>Exponent, fair-value anchor («price X% below fair value on date Y»), floor (lower band),
historical floor breaches.</td></tr>
<tr><td>Accumulation</td><td>Ladder/drip/reserve split, ladder zones, daily drip (and slow), share for the
«flush», weekly anti-miss, accumulation window.</td></tr>
<tr><td>DCA</td><td>Duration, front-load by blocks of months, boosts (drawdown, Fear &amp; Greed, VIX), monthly
boost cap, MA200 kill-switch.</td></tr>
<tr><td>Exit</td><td>Scheduled sales (months after halving), share to hold forever, weekly RSI confirmation,
minimum number of euphoria signals.</td></tr>
<tr><td>Levels</td><td>Upside and downside invalidation levels, cited levels (supports/targets).</td></tr>
<tr><td>Statistics and seasonality</td><td>Failed rallies, median pullbacks, median returns by month.</td></tr>
<tr><td>Allocation</td><td>BTC/ETH share in the first months, altcoins, rules such as «no leverage» or
«never buy rallies».</td></tr>
</table>
<h3>4.3 Checking the results (Tools → Documents and parameters…)</h3>
<ul>
<li><b>Documents:</b> title, date, source (author or site), number of insights extracted, flags.
Selecting a document shows its insights below: category, parameter, value, page and <b>evidence</b>
(the original text excerpt). Hover a cell for the full text.</li>
<li><b>Flags:</b> «promotional» (the document leads to paid content: the track records cited are
self-reported), «disclaimer: not financial advice», «small statistical samples declared».</li>
<li><b>Parameters:</b> the effective strategy. For each parameter: value used, source document, date and
<b>Conflicts</b> (different values proposed by other documents). The most recent document always wins.</li>
<li><b>Remove</b> deletes the selected document; <b>Re-analyze all</b> re-applies the extraction rules to
all saved documents (useful after a program update).</li>
</ul>
<p class="tip">If an extracted value does not match what you read in the PDF, the evidence shows how it
was read: you can then tell whether the document uses wording the rules do not recognize. In that case
the plan falls back to the default value.</p>

<h2>5. Plan tab: the fields to fill in</h2>
<h3>5.1 Capital and market</h3>
<table>
<tr><th>Field</th><th>Meaning</th></tr>
<tr><td>Capital</td><td>Total amount you intend to allocate to the plan, in the chosen currency. It must be
money you can leave untouched for 4+ years, separate from your emergency fund.</td></tr>
<tr><td>Currency</td><td>EUR or USD. The plan reasons in dollars (the documents' prices are in USD) and
converts using the stated exchange rate.</td></tr>
<tr><td>USD per 1 unit</td><td>How many dollars 1 unit of the capital currency is worth (e.g. 1.17 for EUR).
With USD it is locked at 1. It updates with market data.</td></tr>
<tr><td>BTC price (USD)</td><td>Reference price for all calculations. Filled by «Refresh market data» or by
hand.</td></tr>
<tr><td>Refresh market data</td><td>Downloads from CoinGecko the price, the USD/EUR rate and 365 days of daily
closes (from which it computes 200-day MA, 200-day high and cycle closing low) and the Fear &amp; Greed
index from alternative.me. If a service does not answer, the fields stay unchanged and a warning
appears.</td></tr>
<tr><td>Date</td><td>Analysis date: determines where you are in the cycle. Normally today, but you can
simulate other dates.</td></tr>
</table>
<h3>5.2 Strategy</h3>
<table>
<tr><th>Field</th><th>Meaning</th></tr>
<tr><td>Profile</td><td><b>Prudent</b>: 40% of capital in the «bottom window», no altcoins/ETH. <b>Balanced</b>:
50%, up to 20% altcoins and 10% ETH. <b>Aggressive</b>: 60%, up to 30% altcoins and 20% ETH. The effective
limits are the lower of the profile and the documents.</td></tr>
<tr><td>Bottom-window share</td><td>Percentage of capital devoted to ladder + drip + reserve (the «bottom
window»). «From profile» uses the profile's value. The rest goes to the extended DCA.</td></tr>
<tr><td>Re-anchor ladder to current floor</td><td>The ladder's price zones are written for a power-law floor
at a certain date. With this option they are shifted in proportion to today's floor (factor shown in the
plan). If off, they stay at the document's prices.</td></tr>
<tr><td>Slow drip (half)</td><td>Halves the drip's daily percentage (e.g. from 1% to 0.5% of capital per
day), lengthening the buying period.</td></tr>
</table>
<h3>5.3 Indicators (optional)</h3>
<p>They activate the documents' conditional rules. If an indicator is «n/a» the related rule cannot be
evaluated and the plan says so.</p>
<table>
<tr><th>Field</th><th>What it is for</th></tr>
<tr><td>Fear &amp; Greed</td><td>Sentiment index 0–100 (0 = extreme fear). Below the document's threshold
(normally 25) it activates a DCA boost.</td></tr>
<tr><td>200-day MA</td><td>Simple 200-day moving average of closes. Used by the kill-switch: if the price
exceeds the MA200 by more than a certain percentage (normally 40%) the boosts are suspended.</td></tr>
<tr><td>200-day high</td><td>The highest close of the last 200 days. If the price is at or beyond the
threshold distance from it (normally 20%) a boost is activated.</td></tr>
<tr><td>VIX</td><td>US equity volatility index. Above the threshold (normally 25) a boost is activated. It is
not downloaded automatically.</td></tr>
<tr><td>Cycle closing low</td><td>The lowest daily close after the year's high. A ladder rung triggers only on a
daily close below this level («new low»), not on an intraday candle.</td></tr>
</table>
<h3>5.4 Buttons</h3>
<ul>
<li><b>Generate plan</b> (Ctrl+G): computes and shows the report. It is also recomputed when you import
documents or refresh the market.</li>
<li><b>Export HTML / Markdown</b>: saves the report to a file (also from <i>File</i>).</li>
</ul>

<h2>6. How to read the generated plan</h2>
<p>The report is divided into sections, always in the same order. Some appear only when relevant to the
cycle phase.</p>
<h3>6.1 What to do now</h3>
<p>A short operational list generated by the rules: purchases for active rungs, drip status, anti-miss
reminder, first DCA installment with any boost, or «no purchases» if you are in a rally or peak phase.
Read this section first.</p>
<h3>6.2 Market and cycle situation</h3>
<table>
<tr><th>Item</th><th>Meaning</th></tr>
<tr><td>Last halving</td><td>Date of the last halving of the block reward, days and months elapsed. The 4-year
cycle is measured from here (denoted «H»).</td></tr>
<tr><td>Cycle phase</td><td>Classification based on months since the halving: <b>Post-halving rally</b>, <b>Peak
window</b> (around the peak month), <b>Bear market</b>, <b>Bottom window</b>, <b>Accumulation</b> (after the
low, before the halving), <b>Pre-halving</b>. With default values: peak H+18 months, low H+30, accumulation
H+30→H+48.</td></tr>
<tr><td>Estimated low (H+offset)</td><td>Expected low date: last halving + the document's months.</td></tr>
<tr><td>Bottom window</td><td>Interval in which the document expects purchases to concentrate (from the
document, otherwise estimated low ±3 months).</td></tr>
<tr><td>Low from high + 12/13 months</td><td>Alternative low estimate: the cycle high's date plus the average
months observed in past cycles.</td></tr>
<tr><td>Cycle high</td><td>All-time high of the current cycle and <b>drawdown</b> (percentage decline of the
current price from it).</td></tr>
<tr><td>Power law fair value</td><td>The power-law model's «theoretical» value at today's date and the
price's percentage distance (negative = below).</td></tr>
<tr><td>Power law floor</td><td>The model's lower band (normally about 42% of fair value) and the price's
distance. It is not guaranteed support.</td></tr>
<tr><td>Next halving</td><td>(Estimated) date of the next halving, basis of the exit plan.</td></tr>
</table>
<h3>6.3 Capital allocation</h3>
<p>Splits the capital into: <b>bottom window</b> (ladder + drip + reserve), <b>extended DCA</b> and
<b>unallocated</b>. In rally/peak phases all capital is «unallocated» (no purchases); the «bottom window»
share is zero if the window is closed or you are already in the accumulation phase.</p>
<h3>6.4 Bottom window: ladder, drip and reserve</h3>
<p>The window's capital is split into three streams (normally 50% ladder, 30% drip, 20% reserve).</p>
<ul>
<li><b>Ladder.</b> Descending price zones, each with a percentage of the window's capital. Table:
<i>#</i> rung; <i>Zone</i> price range (the last one is «&lt; X», with no lower limit); <i>% of capital</i> (with
«+ flush reserve» on the last rung); <i>Amount</i> in your currency; <i>Est. BTC</i> if bought at mid-zone;
<i>Triggers at ≤</i> the daily-close level that activates the purchase; <i>Status</i>: «IN ZONE now», «below the
zone (buyable)» or «waiting (x% from price)». Key rule: a rung triggers on a <b>daily close</b> below the
cycle's closing low, not on an intraday spike. Never buy rallies.</li>
<li><b>Drip (daily purchase).</b> A small percentage of capital (normally 1% per day, 0.5% if «slow») bought
each day while the price is <b>below the power-law floor</b>. The plan shows daily amount, total budget,
duration in days and status (ACTIVE / paused).</li>
<li><b>Reserve.</b> Part kept as ammunition: a portion (normally 10% of the window's capital) is meant for
a violent «<b>flush</b>», i.e. the last rung; the rest is <b>backstop</b>.</li>
<li><b>Anti-miss.</b> If the market has not offered the expected zones, from the last 4 weeks of the window
the uninvested capital is spread over weekly installments (at least a small percentage, normally 3%) by
the end of the window, so as not to stay out of the market.</li>
</ul>
<h3>6.5 Extended front-loaded DCA</h3>
<p>The capital not assigned to the window is invested with a monthly <b>front-loaded</b> <b>DCA</b>
(periodic buying): higher installments at the start, decreasing. With default values: 40% in months 1–3,
30% in months 4–6, 20% in months 7–9, 10% in months 10–12. It starts at H+30 months or today if already
past.</p>
<table>
<tr><th>Item</th><th>Meaning</th></tr>
<tr><td>Base installment</td><td>Monthly amount according to the front-load.</td></tr>
<tr><td>Max installment with boost</td><td>Base installment increased by the maximum boost cap (normally
+50%).</td></tr>
<tr><td>Boost</td><td>Installment increases when conditions are active: drawdown from the 200-day high (≥20%),
Fear &amp; Greed below 25, VIX above 25: each +25%, with a total monthly cap (+50%). Boosts do not add
capital: they <b>pull forward the final installments</b> (the plan gets shorter).</td></tr>
<tr><td>Active now</td><td>YES / no / n/a (missing indicator).</td></tr>
<tr><td>Kill-switch</td><td>If the price exceeds the MA200 by more than 40% (document value) the boosts are
suspended: the market is considered overheated.</td></tr>
</table>
<h3>6.6 What to buy</h3>
<p>Composition of purchases: in the first months almost only BTC (with ETH up to the profile's limit), then
any «top-N» altcoins only with BTC's weekly trend up; avoid ranks 51–100. No leverage.</p>
<h3>6.7 Exit plan (next cycle)</h3>
<p>Scheduled staged sales relative to the <b>next</b> halving (normally H+12, H+15, H+18 months, 25% of the
position each), with the <b>share never sold</b> («moon bag», normally 25%). The notes indicate: expected peak
window (halving + 500–550 days), secondary confirmation with weekly RSI above a threshold (normally 80),
selling without hesitation if 3+ euphoria signals appear within the window, and partial profit-taking on a
new all-time high.</p>
<h3>6.8 Levels that decide the scenario</h3>
<p><b>Upside invalidation level</b>: a close above means the downtrend is over (switch to plain DCA).
<b>Downside level</b>: a close below means the final leg of the decline (use the ladder). The plan shows
the percentage distance from price or «BROKEN».</p>
<h3>6.9 Scenarios and low estimates by source</h3>
<ul>
<li><b>Low scenario</b>: low hypotheses (price and drawdown from the high): conservative, base, aggressive.</li>
<li><b>Implied peak</b>: from the assumed low, the peak corresponding to the expected historical gains
(e.g. +200% … +400%).</li>
<li><b>Stated peak target</b>: if present in the document.</li>
<li><b>Low estimates by source</b>: each document with its own price range; it shows how much the sources
diverge.</li>
</ul>
<h3>6.10 Warnings (critical partner)</h3>
<p>A list of risks generated from the data. Do not ignore it:</p>
<ul>
<li><b>Single source:</b> all documents by the same author → confirmation-bias risk.</li>
<li><b>Promotional content</b> and self-reported track records.</li>
<li><b>Diverging low estimates</b>; <b>model inconsistency</b> (e.g. a low range implying a floor break).</li>
<li><b>Small sample:</b> the «4-year cycle» rests on 4 observations; ETFs and institutions may change its
timing and size.</li>
<li><b>Dates that are too well known:</b> if everyone knows the window, it may be front-run.</li>
<li><b>The floor is not guaranteed:</b> it has been broken in the past; the equivalent price is shown.</li>
<li><b>Stress test:</b> estimated average ladder price and the loss if BTC fell to the broken floor.</li>
<li><b>Diminishing returns</b> cycle after cycle and <b>incomplete market data</b>.</li>
</ul>
<h3>6.11 Sources and parameters used</h3>
<p>List of the documents (title, date, source) and a table of every parameter actually used, with value and
source document («default» if not present in the documents). It lets you reproduce and verify every
number in the plan.</p>

<h2>7. Chart tab</h2>
<h3>7.1 What it shows</h3>
<table>
<tr><th>Element</th><th>Meaning</th></tr>
<tr><td>Black line</td><td>Daily closes of the BTC price (last 365 days).</td></tr>
<tr><td>Orange line</td><td>Current price (updates every 60 seconds, only while the tab is visible).</td></tr>
<tr><td>Green bands «Ladder n»</td><td>The ladder's buy zones, with range and percentage of capital.</td></tr>
<tr><td>Dashed grey / green curves</td><td>Power-law fair value and floor, projected into the future. Beyond the
data horizon they are model extrapolations.</td></tr>
<tr><td>Blue line «MA200»</td><td>200-day moving average (if entered in the plan).</td></tr>
<tr><td>Dashed red level lines</td><td>Upside/downside invalidation levels.</td></tr>
<tr><td>Orange band «Bottom window» and line «Estimated bottom»</td><td>Expected period and date of the
cycle low.</td></tr>
<tr><td>Bar above the chart</td><td>Price, nearest ladder rung and distance, rally from the cycle low compared with
the median failed rally (+35%, 15 cases: context only), update status.</td></tr>
<tr><td>Bottom line</td><td>Sources used and the «third-party estimates, not forecasts» notice.</td></tr>
</table>
<h3>7.2 Controls</h3>
<ul>
<li><b>Logarithmic scale:</b> on a log scale equal distances represent equal percentage changes; it is the right
scale for comparing different cycles. The axes show powers of 10 (e.g. 9·10⁴ = 90,000).</li>
<li><b>Show exits:</b> extends the axis to the scheduled sales. It shows the vertical lines «Sell 25% · 75% left»,
the <b>peak window</b> and the stated <b>peak target</b>. Exits are by date, not by price: the prices are only
estimates (target and scenarios).</li>
<li><b>Left-click</b> a point: draws the price and date lines at that point, with a label (date, price,
difference from the current price). <b>Right-click</b>: removes them.</li>
<li><b>Mouse wheel / drag:</b> zoom and pan. <b>Reset view</b> restores the initial framing.</li>
<li><b>Refresh history:</b> downloads the 365 days of closes again.</li>
<li><b>Export image… / Copy:</b> saves or copies as PNG the chart with status bar and sources (without
buttons), ready to share. Enlarge the window for a sharper image.</li>
</ul>

<h2>8. Menus, language, updates and saved data</h2>
<table>
<tr><th>Menu</th><th>Items</th></tr>
<tr><td>File</td><td>Import documents… (Ctrl+O), Import folder…, Export plan (HTML/Markdown), Quit.</td></tr>
<tr><td>Data</td><td>Refresh market data (F5), Generate plan (Ctrl+G), Re-analyze all documents, Remove
selected document, Open data folder.</td></tr>
<tr><td>Tools</td><td>Documents and parameters…, Language (Italiano / English: applied on the next
start).</td></tr>
<tr><td>Help</td><td>Guide (window with index and search, F1), Guide (PDF) (this document), Check for updates, About (author and version).</td></tr>
</table>
<ul>
<li><b>Language:</b> on first start it follows the system language (Italian if it, otherwise English). The
plan, the export and this guide follow the chosen language.</li>
<li><b>Updates:</b> at startup the program checks GitHub releases in the background and, if a newer version
is available, asks whether to download and install it. The manual check is in <i>Help → Check for
updates</i>.</li>
<li><b>Saved data:</b> the knowledge base (documents and parameters) and the settings (capital, currency,
profile, indicators, chart preferences) stay on your computer. <i>Data → Open data folder</i> opens the
folder; nothing is sent to external servers, except the requests to CoinGecko, alternative.me and
GitHub.</li>
</ul>

<h2>9. Glossary</h2>
<table>
<tr><th>Term</th><th>Meaning</th></tr>
<tr><td>Halving (H)</td><td>Halving of the block reward, every 210,000 blocks (about 4 years). Dates: 2012,
2016, 2020, 2024; next estimated April 2028. «H+18» = 18 months after the halving.</td></tr>
<tr><td>4-year cycle</td><td>Observed pattern of rally, peak, decline and low tied to the halvings. Based on only
4 cycles.</td></tr>
<tr><td>Power law</td><td>Model linking price to the days since the genesis block (3 January 2009): price = A ×
days^B (standard exponent 5.82).</td></tr>
<tr><td>Fair value / floor</td><td>The model's central value / lower band (normally ~42% of fair value).</td></tr>
<tr><td>Drawdown</td><td>Percentage decline from the previous high.</td></tr>
<tr><td>DCA</td><td>Dollar-cost averaging: periodic purchases of a fixed amount.</td></tr>
<tr><td>Front-loaded</td><td>DCA with higher installments at the start of the period.</td></tr>
<tr><td>Ladder</td><td>A series of orders at descending price levels.</td></tr>
<tr><td>Drip</td><td>Small daily purchase while the price is below the floor.</td></tr>
<tr><td>Flush</td><td>Violent, rapid price collapse; the reserve is meant to exploit it.</td></tr>
<tr><td>Backstop</td><td>Part of the reserve not meant for the flush, used as a safety net.</td></tr>
<tr><td>Anti-miss</td><td>Rule that requires investing the remainder in weekly installments near the end of the
window.</td></tr>
<tr><td>Boost</td><td>Temporary increase of the DCA installment when stress conditions are active.</td></tr>
<tr><td>Kill-switch</td><td>Condition that suspends the boosts (price far above the MA200).</td></tr>
<tr><td>MA200</td><td>Simple 200-day moving average.</td></tr>
<tr><td>Fear &amp; Greed</td><td>Market sentiment index from 0 (extreme fear) to 100 (extreme greed).</td></tr>
<tr><td>VIX</td><td>Implied-volatility index of the S&amp;P 500, a macro stress indicator.</td></tr>
<tr><td>Weekly RSI</td><td>14-period momentum indicator on weekly candles; above 80 = overheated.</td></tr>
<tr><td>Moon bag</td><td>Share of the position that is never sold.</td></tr>
<tr><td>Invalidation</td><td>Level beyond which the base scenario is no longer valid.</td></tr>
<tr><td>Front-running</td><td>Anticipating the market's moves on very well-known dates/levels.</td></tr>
<tr><td>Daily close</td><td>Closing price of the daily candle (not the intraday low).</td></tr>
<tr><td>Knowledge base</td><td>Local archive of the imported documents and extracted parameters.</td></tr>
<tr><td>Insight</td><td>A single piece of information extracted from a document, with page and evidence.</td></tr>
</table>

<h2>10. Limits, warnings and troubleshooting</h2>
<h3>Limits of the method</h3>
<ul>
<li>Extraction uses rules on English text and on the format of known documents; other documents may be
read only partially.</li>
<li>The model assumes the future will resemble 4 past cycles. Markets change.</li>
<li>Market data is free and may be delayed or rate-limited.</li>
<li>The plan does not know your tax situation, your horizon or your risk tolerance.</li>
</ul>
<h3>Common problems</h3>
<table>
<tr><th>Problem</th><th>What to do</th></tr>
<tr><td>«Generate plan» says capital and price must be greater than zero</td><td>Fill in Capital and BTC price (or
press «Refresh market data»).</td></tr>
<tr><td>No extractable text in the PDF</td><td>The PDF is an image: convert it with OCR or use a text
version.</td></tr>
<tr><td>Market data download failed</td><td>Check your connection; the free service may limit requests: retry after
a minute, or enter the values by hand.</td></tr>
<tr><td>A parameter shows the default value</td><td>The document does not contain it or it was not recognized: check
the evidence in <i>Tools → Documents and parameters…</i>.</td></tr>
<tr><td>After an update the data looks old</td><td>Use <i>Data → Re-analyze all documents</i>.</td></tr>
<tr><td>The chart does not update</td><td>Polling happens only while the tab is visible; press «Refresh
history».</td></tr>
<tr><td>The language does not change</td><td>The language applies when the application is restarted.</td></tr>
</table>
<p class="note"><b>Remember:</b> educational tool, not financial advice. No model removes the risk of losing
capital.</p>
"""
