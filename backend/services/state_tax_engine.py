"""
State Income Tax Engine — All 50 US States + DC (2024 tax year)
Covers: flat taxes, graduated brackets, no-income-tax states,
        standard deductions, personal exemptions, and special rules.
"""

from dataclasses import dataclass, field
from typing import Optional

# ─── Data Structures ────────────────────────────────────────────

@dataclass
class StateTaxConfig:
    name: str
    code: str
    has_income_tax: bool = True
    flat_rate: Optional[float] = None          # e.g. 0.05 for 5% flat
    brackets_single: list = field(default_factory=list)   # [(cap, rate), ...]
    brackets_joint:  list = field(default_factory=list)
    standard_deduction_single: float = 0.0
    standard_deduction_joint:  float = 0.0
    personal_exemption_single: float = 0.0
    personal_exemption_joint:  float = 0.0
    notes: str = ""

# ─── All 50 States + DC ─────────────────────────────────────────

STATE_TAX_DATA: dict[str, StateTaxConfig] = {

    # ── No income tax states ────────────────────────────────────
    "AK": StateTaxConfig("Alaska",       "AK", has_income_tax=False),
    "FL": StateTaxConfig("Florida",      "FL", has_income_tax=False),
    "NV": StateTaxConfig("Nevada",       "NV", has_income_tax=False),
    "NH": StateTaxConfig("New Hampshire","NH", has_income_tax=False,
          notes="Tax on interest/dividends only, being phased out"),
    "SD": StateTaxConfig("South Dakota", "SD", has_income_tax=False),
    "TN": StateTaxConfig("Tennessee",    "TN", has_income_tax=False,
          notes="Hall Tax on dividends fully repealed 2021"),
    "TX": StateTaxConfig("Texas",        "TX", has_income_tax=False),
    "WA": StateTaxConfig("Washington",   "WA", has_income_tax=False,
          notes="7% capital gains tax on gains >$262,000 (2024)"),
    "WY": StateTaxConfig("Wyoming",      "WY", has_income_tax=False),

    # ── Flat-rate states ────────────────────────────────────────
    "AZ": StateTaxConfig("Arizona",      "AZ", flat_rate=0.025,
          standard_deduction_single=13_850, standard_deduction_joint=27_700,
          notes="Flat 2.5% (2024)"),
    "CO": StateTaxConfig("Colorado",     "CO", flat_rate=0.044,
          standard_deduction_single=0, personal_exemption_single=0,
          notes="Flat 4.4%"),
    "IL": StateTaxConfig("Illinois",     "IL", flat_rate=0.0495,
          personal_exemption_single=2_425, personal_exemption_joint=4_850,
          notes="Flat 4.95%"),
    "IN": StateTaxConfig("Indiana",      "IN", flat_rate=0.0305,
          personal_exemption_single=1_000, personal_exemption_joint=2_000,
          notes="Flat 3.05% (2024); counties add 0.5–2.9%"),
    "KY": StateTaxConfig("Kentucky",     "KY", flat_rate=0.04,
          standard_deduction_single=3_160, standard_deduction_joint=3_160,
          notes="Flat 4%"),
    "MA": StateTaxConfig("Massachusetts","MA", flat_rate=0.05,
          personal_exemption_single=4_400, personal_exemption_joint=8_800,
          notes="5% flat; 9% on long-term capital gains"),
    "MI": StateTaxConfig("Michigan",     "MI", flat_rate=0.0425,
          personal_exemption_single=5_400, personal_exemption_joint=10_800,
          notes="Flat 4.25%"),
    "NC": StateTaxConfig("North Carolina","NC", flat_rate=0.045,
          standard_deduction_single=12_750, standard_deduction_joint=25_500,
          notes="Flat 4.5% (2024)"),
    "PA": StateTaxConfig("Pennsylvania", "PA", flat_rate=0.0307,
          notes="Flat 3.07%; no standard deduction"),
    "UT": StateTaxConfig("Utah",         "UT", flat_rate=0.0465,
          personal_exemption_single=1_802, personal_exemption_joint=3_604,
          notes="Flat 4.65%"),

    # ── Graduated bracket states ────────────────────────────────
    "AL": StateTaxConfig("Alabama", "AL",
        brackets_single=[
            (500,    0.02),
            (3_000,  0.04),
            (float("inf"), 0.05),
        ],
        brackets_joint=[
            (1_000,  0.02),
            (6_000,  0.04),
            (float("inf"), 0.05),
        ],
        standard_deduction_single=2_500,
        standard_deduction_joint=7_500,
        personal_exemption_single=1_500,
        personal_exemption_joint=3_000,
    ),
    "AR": StateTaxConfig("Arkansas", "AR",
        brackets_single=[
            (4_300,  0.02),
            (8_500,  0.04),
            (float("inf"), 0.044),
        ],
        standard_deduction_single=2_200,
        standard_deduction_joint=4_400,
        personal_exemption_single=29,
        personal_exemption_joint=58,
    ),
    "CA": StateTaxConfig("California", "CA",
        brackets_single=[
            (10_412,  0.01),
            (24_684,  0.02),
            (38_959,  0.04),
            (54_081,  0.06),
            (68_350,  0.08),
            (349_137, 0.093),
            (418_961, 0.103),
            (698_274, 0.113),
            (float("inf"), 0.123),
        ],
        brackets_joint=[
            (20_824,  0.01),
            (49_368,  0.02),
            (77_918,  0.04),
            (108_162, 0.06),
            (136_700, 0.08),
            (698_274, 0.093),
            (837_922, 0.103),
            (1_000_000, 0.113),
            (float("inf"), 0.123),
        ],
        standard_deduction_single=5_202,
        standard_deduction_joint=10_404,
        personal_exemption_single=144,
        personal_exemption_joint=288,
        notes="Additional 1% Mental Health Services Tax on income >$1M",
    ),
    "CT": StateTaxConfig("Connecticut", "CT",
        brackets_single=[
            (10_000,  0.03),
            (50_000,  0.05),
            (100_000, 0.055),
            (200_000, 0.06),
            (250_000, 0.065),
            (500_000, 0.069),
            (float("inf"), 0.0699),
        ],
        brackets_joint=[
            (20_000,  0.03),
            (100_000, 0.05),
            (200_000, 0.055),
            (400_000, 0.06),
            (500_000, 0.065),
            (1_000_000, 0.069),
            (float("inf"), 0.0699),
        ],
        personal_exemption_single=15_000,
        personal_exemption_joint=24_000,
    ),
    "DC": StateTaxConfig("District of Columbia", "DC",
        brackets_single=[
            (10_000,  0.04),
            (40_000,  0.06),
            (60_000,  0.065),
            (250_000, 0.085),
            (500_000, 0.0925),
            (1_000_000, 0.0975),
            (float("inf"), 0.1075),
        ],
        standard_deduction_single=12_950,
        standard_deduction_joint=25_900,
    ),
    "DE": StateTaxConfig("Delaware", "DE",
        brackets_single=[
            (2_000,  0.0),
            (5_000,  0.022),
            (10_000, 0.039),
            (20_000, 0.048),
            (25_000, 0.052),
            (60_000, 0.055),
            (float("inf"), 0.066),
        ],
        standard_deduction_single=3_250,
        standard_deduction_joint=6_500,
        personal_exemption_single=110,
        personal_exemption_joint=220,
    ),
    "GA": StateTaxConfig("Georgia", "GA",
        flat_rate=0.054,   # Flat 5.49% (2024, down from graduated)
        standard_deduction_single=12_000,
        standard_deduction_joint=24_000,
        notes="Moved to flat 5.49% in 2024",
    ),
    "HI": StateTaxConfig("Hawaii", "HI",
        brackets_single=[
            (2_400,   0.014),
            (4_800,   0.032),
            (9_600,   0.055),
            (14_400,  0.064),
            (19_200,  0.068),
            (24_000,  0.072),
            (36_000,  0.076),
            (48_000,  0.079),
            (150_000, 0.0825),
            (175_000, 0.09),
            (200_000, 0.10),
            (float("inf"), 0.11),
        ],
        brackets_joint=[
            (4_800,   0.014),
            (9_600,   0.032),
            (19_200,  0.055),
            (28_800,  0.064),
            (38_400,  0.068),
            (48_000,  0.072),
            (72_000,  0.076),
            (96_000,  0.079),
            (300_000, 0.0825),
            (350_000, 0.09),
            (400_000, 0.10),
            (float("inf"), 0.11),
        ],
        standard_deduction_single=2_200,
        standard_deduction_joint=4_400,
        personal_exemption_single=1_144,
        personal_exemption_joint=2_288,
    ),
    "IA": StateTaxConfig("Iowa", "IA",
        brackets_single=[
            (6_000,  0.044),
            (30_000, 0.0482),
            (float("inf"), 0.057),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
        notes="Iowa conforms to federal standard deduction in 2024",
    ),
    "ID": StateTaxConfig("Idaho", "ID",
        brackets_single=[
            (4_489,  0.0),
            (float("inf"), 0.058),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
        notes="Flat 5.8% above exemption",
    ),
    "KS": StateTaxConfig("Kansas", "KS",
        brackets_single=[
            (15_000, 0.031),
            (30_000, 0.0525),
            (float("inf"), 0.057),
        ],
        brackets_joint=[
            (30_000, 0.031),
            (60_000, 0.0525),
            (float("inf"), 0.057),
        ],
        standard_deduction_single=3_500,
        standard_deduction_joint=8_000,
        personal_exemption_single=2_250,
        personal_exemption_joint=4_500,
    ),
    "LA": StateTaxConfig("Louisiana", "LA",
        brackets_single=[
            (12_500, 0.0185),
            (50_000, 0.035),
            (float("inf"), 0.0425),
        ],
        brackets_joint=[
            (25_000, 0.0185),
            (100_000, 0.035),
            (float("inf"), 0.0425),
        ],
        personal_exemption_single=4_500,
        personal_exemption_joint=9_000,
    ),
    "ME": StateTaxConfig("Maine", "ME",
        brackets_single=[
            (24_500, 0.058),
            (58_050, 0.0675),
            (float("inf"), 0.0715),
        ],
        brackets_joint=[
            (49_050, 0.058),
            (116_100, 0.0675),
            (float("inf"), 0.0715),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
        personal_exemption_single=5_000,
        personal_exemption_joint=10_000,
    ),
    "MD": StateTaxConfig("Maryland", "MD",
        brackets_single=[
            (1_000,   0.02),
            (2_000,   0.03),
            (3_000,   0.04),
            (100_000, 0.0475),
            (125_000, 0.05),
            (150_000, 0.0525),
            (250_000, 0.055),
            (float("inf"), 0.0575),
        ],
        brackets_joint=[
            (1_000,   0.02),
            (2_000,   0.03),
            (3_000,   0.04),
            (150_000, 0.0475),
            (175_000, 0.05),
            (225_000, 0.0525),
            (300_000, 0.055),
            (float("inf"), 0.0575),
        ],
        standard_deduction_single=2_400,
        standard_deduction_joint=4_800,
        personal_exemption_single=3_200,
        personal_exemption_joint=6_400,
        notes="County/city taxes add 2.25–3.2%",
    ),
    "MN": StateTaxConfig("Minnesota", "MN",
        brackets_single=[
            (30_070,  0.0535),
            (98_760,  0.068),
            (183_340, 0.0785),
            (float("inf"), 0.0985),
        ],
        brackets_joint=[
            (43_950,  0.0535),
            (174_610, 0.068),
            (304_970, 0.0785),
            (float("inf"), 0.0985),
        ],
        standard_deduction_single=14_575,
        standard_deduction_joint=29_150,
        personal_exemption_single=4_800,
        personal_exemption_joint=9_600,
    ),
    "MO": StateTaxConfig("Missouri", "MO",
        brackets_single=[
            (1_121,  0.0),
            (2_242,  0.015),
            (3_363,  0.02),
            (4_484,  0.025),
            (5_605,  0.03),
            (6_726,  0.035),
            (7_847,  0.04),
            (8_968,  0.045),
            (float("inf"), 0.048),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
    ),
    "MS": StateTaxConfig("Mississippi", "MS",
        brackets_single=[
            (10_000, 0.0),
            (float("inf"), 0.047),
        ],
        standard_deduction_single=2_300,
        standard_deduction_joint=4_600,
        personal_exemption_single=6_000,
        personal_exemption_joint=12_000,
        notes="Moving toward flat 4% by 2026",
    ),
    "MT": StateTaxConfig("Montana", "MT",
        brackets_single=[
            (3_600,  0.01),
            (6_300,  0.02),
            (9_700,  0.03),
            (13_000, 0.04),
            (16_800, 0.05),
            (21_600, 0.06),
            (float("inf"), 0.069),
        ],
        standard_deduction_single=5_540,
        standard_deduction_joint=11_080,
        personal_exemption_single=2_760,
        personal_exemption_joint=5_520,
    ),
    "NE": StateTaxConfig("Nebraska", "NE",
        brackets_single=[
            (3_700,  0.0246),
            (22_170, 0.0351),
            (35_730, 0.0501),
            (float("inf"), 0.0584),
        ],
        brackets_joint=[
            (7_390,  0.0246),
            (44_350, 0.0351),
            (71_460, 0.0501),
            (float("inf"), 0.0584),
        ],
        standard_deduction_single=7_900,
        standard_deduction_joint=15_800,
        personal_exemption_single=157,
        personal_exemption_joint=314,
    ),
    "NJ": StateTaxConfig("New Jersey", "NJ",
        brackets_single=[
            (20_000,  0.014),
            (35_000,  0.0175),
            (40_000,  0.035),
            (75_000,  0.05525),
            (500_000, 0.0637),
            (1_000_000, 0.0897),
            (float("inf"), 0.1075),
        ],
        brackets_joint=[
            (20_000,  0.014),
            (50_000,  0.0175),
            (70_000,  0.0245),
            (80_000,  0.035),
            (150_000, 0.05525),
            (500_000, 0.0637),
            (1_000_000, 0.0897),
            (float("inf"), 0.1075),
        ],
        personal_exemption_single=1_000,
        personal_exemption_joint=2_000,
    ),
    "NM": StateTaxConfig("New Mexico", "NM",
        brackets_single=[
            (5_500,   0.017),
            (11_000,  0.032),
            (16_000,  0.047),
            (210_000, 0.049),
            (float("inf"), 0.059),
        ],
        brackets_joint=[
            (8_000,   0.017),
            (16_000,  0.032),
            (24_000,  0.047),
            (315_000, 0.049),
            (float("inf"), 0.059),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
    ),
    "NY": StateTaxConfig("New York", "NY",
        brackets_single=[
            (8_500,   0.04),
            (11_700,  0.045),
            (13_900,  0.0525),
            (80_650,  0.055),
            (215_400, 0.06),
            (1_077_550, 0.0685),
            (5_000_000, 0.0965),
            (25_000_000, 0.103),
            (float("inf"), 0.109),
        ],
        brackets_joint=[
            (17_150,  0.04),
            (23_600,  0.045),
            (27_900,  0.0525),
            (161_550, 0.055),
            (323_200, 0.06),
            (2_155_350, 0.0685),
            (5_000_000, 0.0965),
            (25_000_000, 0.103),
            (float("inf"), 0.109),
        ],
        standard_deduction_single=8_000,
        standard_deduction_joint=16_050,
        personal_exemption_single=0,
        notes="NYC adds 3.078–3.876%; Yonkers adds 1.61625%",
    ),
    "OH": StateTaxConfig("Ohio", "OH",
        brackets_single=[
            (26_050,  0.0),
            (46_100,  0.02765),
            (92_150,  0.03226),
            (115_300, 0.03688),
            (float("inf"), 0.03990),
        ],
        personal_exemption_single=2_400,
        personal_exemption_joint=4_800,
        notes="Cities levy their own income taxes (typically 1–3%)",
    ),
    "OK": StateTaxConfig("Oklahoma", "OK",
        brackets_single=[
            (1_000,  0.0025),
            (2_500,  0.0075),
            (3_750,  0.0175),
            (4_900,  0.0275),
            (7_200,  0.0375),
            (float("inf"), 0.0475),
        ],
        brackets_joint=[
            (2_000,  0.0025),
            (5_000,  0.0075),
            (7_500,  0.0175),
            (9_800,  0.0275),
            (12_200, 0.0375),
            (float("inf"), 0.0475),
        ],
        standard_deduction_single=6_350,
        standard_deduction_joint=12_700,
        personal_exemption_single=1_000,
        personal_exemption_joint=2_000,
    ),
    "OR": StateTaxConfig("Oregon", "OR",
        brackets_single=[
            (4_050,   0.0475),
            (10_200,  0.0675),
            (125_000, 0.0875),
            (float("inf"), 0.099),
        ],
        brackets_joint=[
            (8_100,   0.0475),
            (20_400,  0.0675),
            (250_000, 0.0875),
            (float("inf"), 0.099),
        ],
        standard_deduction_single=2_420,
        standard_deduction_joint=4_865,
        personal_exemption_single=236,
        personal_exemption_joint=472,
        notes="Statewide transit tax 0.1%; Metro/Multnomah add up to 3%",
    ),
    "RI": StateTaxConfig("Rhode Island", "RI",
        brackets_single=[
            (73_450,  0.0375),
            (166_950, 0.0475),
            (float("inf"), 0.0599),
        ],
        standard_deduction_single=10_550,
        standard_deduction_joint=21_150,
        personal_exemption_single=4_850,
        personal_exemption_joint=9_700,
    ),
    "SC": StateTaxConfig("South Carolina", "SC",
        brackets_single=[
            (3_460,  0.0),
            (17_330, 0.03),
            (float("inf"), 0.065),
        ],
        standard_deduction_single=14_600,
        standard_deduction_joint=29_200,
        personal_exemption_single=4_910,
        personal_exemption_joint=9_820,
    ),
    "VT": StateTaxConfig("Vermont", "VT",
        brackets_single=[
            (45_400,  0.0335),
            (110_050, 0.066),
            (229_550, 0.076),
            (float("inf"), 0.0875),
        ],
        brackets_joint=[
            (75_850,  0.0335),
            (183_400, 0.066),
            (279_450, 0.076),
            (float("inf"), 0.0875),
        ],
        standard_deduction_single=7_000,
        standard_deduction_joint=14_350,
        personal_exemption_single=4_850,
        personal_exemption_joint=9_700,
    ),
    "VA": StateTaxConfig("Virginia", "VA",
        brackets_single=[
            (3_000,  0.02),
            (5_000,  0.03),
            (17_000, 0.05),
            (float("inf"), 0.0575),
        ],
        standard_deduction_single=8_000,
        standard_deduction_joint=16_000,
        personal_exemption_single=930,
        personal_exemption_joint=1_860,
    ),
    "WI": StateTaxConfig("Wisconsin", "WI",
        brackets_single=[
            (14_320,  0.035),
            (28_640,  0.044),
            (315_310, 0.053),
            (float("inf"), 0.0765),
        ],
        brackets_joint=[
            (19_090,  0.035),
            (38_190,  0.044),
            (420_420, 0.053),
            (float("inf"), 0.0765),
        ],
        standard_deduction_single=12_110,
        standard_deduction_joint=22_230,
        personal_exemption_single=700,
        personal_exemption_joint=1_400,
    ),
    "WV": StateTaxConfig("West Virginia", "WV",
        brackets_single=[
            (10_000, 0.03),
            (25_000, 0.04),
            (40_000, 0.045),
            (60_000, 0.06),
            (float("inf"), 0.065),
        ],
        personal_exemption_single=2_000,
        personal_exemption_joint=4_000,
        notes="Phasing down to 4.82% flat by 2030",
    ),
}


# ─── Calculation Engine ──────────────────────────────────────────

def calculate_state_tax(
    state_code: str,
    income: float,
    filing_status: str = "single",
    federal_agi: float = 0.0,
    itemized_deductions: float = 0.0,
) -> dict:
    """
    Calculate state income tax for a given state and income.

    Returns a structured dict with:
      - tax_owed, effective_rate, taxable_income
      - deduction info, bracket breakdown, notes
    """
    code = state_code.upper()
    cfg = STATE_TAX_DATA.get(code)

    if not cfg:
        return {"error": f"State '{code}' not found", "tax_owed": 0.0}

    if not cfg.has_income_tax:
        return {
            "state": cfg.name,
            "state_code": code,
            "has_income_tax": False,
            "tax_owed": 0.0,
            "effective_rate": 0.0,
            "taxable_income": income,
            "deduction_amount": 0.0,
            "notes": cfg.notes or f"{cfg.name} has no state income tax.",
            "brackets": [],
        }

    is_joint = filing_status in ("married_joint", "married_filing_jointly")

    # Deductions
    std_ded = cfg.standard_deduction_joint if is_joint else cfg.standard_deduction_single
    pers_ex = cfg.personal_exemption_joint  if is_joint else cfg.personal_exemption_single
    deduction = max(std_ded, itemized_deductions) + pers_ex
    taxable = max(0.0, income - deduction)

    # Choose brackets
    if cfg.flat_rate is not None:
        tax = taxable * cfg.flat_rate
        brackets = [{"rate": f"{cfg.flat_rate*100:.2f}%", "amount": round(tax, 2),
                     "income_range": f"$0 – ∞"}]
    else:
        raw_brackets = cfg.brackets_joint if (is_joint and cfg.brackets_joint) else cfg.brackets_single
        tax = _marginal_tax(taxable, raw_brackets)
        brackets = _bracket_breakdown(taxable, raw_brackets)

    effective_rate = (tax / income * 100) if income > 0 else 0.0

    return {
        "state": cfg.name,
        "state_code": code,
        "has_income_tax": True,
        "gross_income": income,
        "deduction_amount": round(deduction, 2),
        "taxable_income": round(taxable, 2),
        "tax_owed": round(tax, 2),
        "effective_rate": round(effective_rate, 2),
        "brackets": brackets,
        "notes": cfg.notes,
    }


def calculate_combined_tax(
    state_code: str,
    federal_result: dict,
    filing_status: str = "single",
    itemized_deductions: float = 0.0,
) -> dict:
    """
    Combine federal + state tax calculations into one unified summary.
    """
    income = federal_result.get("gross_income", 0.0)
    state_result = calculate_state_tax(
        state_code=state_code,
        income=income,
        filing_status=filing_status,
        federal_agi=income,
        itemized_deductions=itemized_deductions,
    )

    federal_tax = federal_result.get("tax_owed", 0.0)
    state_tax   = state_result.get("tax_owed", 0.0)
    total_tax   = federal_tax + state_tax
    total_rate  = (total_tax / income * 100) if income > 0 else 0.0

    return {
        "income": income,
        "federal": federal_result,
        "state": state_result,
        "combined": {
            "total_tax": round(total_tax, 2),
            "total_effective_rate": round(total_rate, 2),
            "federal_tax": round(federal_tax, 2),
            "state_tax": round(state_tax, 2),
            "federal_pct": round(federal_tax / total_tax * 100, 1) if total_tax else 0,
            "state_pct":   round(state_tax   / total_tax * 100, 1) if total_tax else 0,
        },
    }


def list_states() -> list[dict]:
    """Return all states sorted alphabetically with basic info."""
    return sorted([
        {
            "code": code,
            "name": cfg.name,
            "has_income_tax": cfg.has_income_tax,
            "top_rate": (
                cfg.flat_rate * 100
                if cfg.flat_rate
                else (cfg.brackets_single[-1][1] * 100 if cfg.brackets_single else 0)
            ) if cfg.has_income_tax else 0,
        }
        for code, cfg in STATE_TAX_DATA.items()
    ], key=lambda x: x["name"])


# ─── Helpers ────────────────────────────────────────────────────

def _marginal_tax(income: float, brackets: list) -> float:
    tax, prev = 0.0, 0.0
    for cap, rate in brackets:
        if income <= prev:
            break
        taxable_in_bracket = min(income, cap) - prev
        tax += taxable_in_bracket * rate
        prev = cap
    return tax


def _bracket_breakdown(income: float, brackets: list) -> list:
    result, prev = [], 0.0
    for cap, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, cap) - prev
        result.append({
            "rate": f"{rate*100:.2f}%",
            "amount": round(taxable * rate, 2),
            "income_range": f"${int(prev):,} – {'∞' if cap == float('inf') else f'${int(cap):,}'}",
        })
        prev = cap
    return result
