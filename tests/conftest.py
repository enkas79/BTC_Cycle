import pytest

from btc_cycle.core.knowledge import KnowledgeBase, build_document
from btc_cycle.core.pdf_reader import RawDocument

ROADMAP = """@bitcoin.daily | Not vibes. February 2026 | Not financial advice.
THE MECHANICAL FORMULA Estimated Peak H + 18 months Estimated Bottom H + 30 months
DCA Start Window H + 30 months Primary Accumulation H + 30m → H + 48m
Cycle High $126,272 (Oct 6, 2025) Current Price ~$67,000
Drawdowns get shallower: -93% → -86% → -84% → -77%.
Returns diminish: 54,900% → 13,000% → 2,125% → 713%
PHASE 1 THE BOTTOM $35K–$50K | Q4 2026
Conservative -60% ~$50,000 Matches StanChart call Base Case -67% ~$41,600 Midpoint
Aggressive -72% ~$35,300 Closer to 2022
Months 1–3 40% $10,000 Months 4–6 30% $7,500 Months 7–9 20% $5,000 Months 10–12 10% $2,500
BTC drops -20% from rolling 200-day high +25% Fear & Greed Index below 25 +25%
Macro spike (VIX > 25 or crypto vol spike) +25% MAXIMUM per month +50% cap
Kill-Switch: BTC closes >+40% above 200-day MA → stop boosts.
The next halving: April 2028. window of 500–550 days before the peak.
H + 12 months (Apr 2029) Sell 25% H + 15 months (Jul 2029) Sell 25%
H + 18 months (Oct 2029) Sell 25% Keep 25% Hold forever
Weekly RSI above 80 When 3+ appear alongside the time window. Target: ~$200K
Join the Discord → checkout now"""

ACCUMULATION = """bitcoin-daily.com Compiled July 22, 2026. Aug to Nov the window you ladder across.
50% The level ladder. 30% The daily drip. 20% Dry powder.
First new low, about $55k to $58k 10% About $50k to $55k 13% About $45k to $50k 16%
Below about $45k, a deep flush 11% + reserve
the public power-law floor, which sits near $57,000 to $58,000 today on bitcoin-daily.com.
you buy about 1 percent of your pot. halve it to half a percent a day.
around ten percent, for a single violent flush. a few percent a week.
A new low means a daily close, not a wick. Never chase green."""

POWER_LAW = """bitcoin-daily.com Compiled July 20, 2026. Bitcoin about $64,590, roughly 43% below
the model's fair value. But price has also closed below it. In early 2015 it fell as much as
about a third under the band. In late 2022 it dipped roughly 12 percent below."""

PULLBACK = """@bitcoin.daily The May high $82,833 A daily close above it breaks the sequence.
The July low $57,735 A close below it means the pullback was not a pullback.
set their final low 13.4, 12.0 and 12.4 months after their cycle tops."""


def make_doc(text: str, name: str, meta_date=None):
    raw = RawDocument(path=__import__("pathlib").Path(name), doc_id=name, pages=[text],
                      meta_date=meta_date)
    return build_document(raw)


@pytest.fixture
def kb():
    base = KnowledgeBase()
    base.add(make_doc(ROADMAP, "2026_2030_bitcoin_cycle_roadmap.pdf"))
    base.add(make_doc(ACCUMULATION, "bitcoin-accumulation-plan.pdf"))
    base.add(make_doc(POWER_LAW, "bitcoin-power-law.pdf"))
    base.add(make_doc(PULLBACK, "the-pullback-playbook.pdf", meta_date="2026-08-24"))
    return base
