"""
Tax calculation engine — 2024 US Federal tax brackets.
Computes tax owed, effective rate, and refund/balance due.
"""

TAX_BRACKETS_2024 = {
    "single": [
        (11600,  0.10),
        (47150,  0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
    "married_joint": [
        (23200,  0.10),
        (94300,  0.12),
        (201050, 0.22),
        (383900, 0.24),
        (487450, 0.32),
        (731200, 0.35),
        (float("inf"), 0.37),
    ],
    "married_separate": [
        (11600,  0.10),
        (47150,  0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (365600, 0.35),
        (float("inf"), 0.37),
    ],
    "head_of_household": [
        (16550,  0.10),
        (63100,  0.12),
        (100500, 0.22),
        (191950, 0.24),
        (243700, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
}

STANDARD_DEDUCTION_2024 = {
    "single": 14600,
    "married_joint": 29200,
    "married_separate": 14600,
    "head_of_household": 21900,
}

def calculate_tax(income: float, filing_status: str = "single",
                  itemized_deductions: float = 0.0,
                  federal_withheld: float = 0.0) -> dict:
    """
    Returns a full tax summary dict.
    """
    status = filing_status.lower().replace(" ", "_")
    if status not in TAX_BRACKETS_2024:
        status = "single"

    std_deduction = STANDARD_DEDUCTION_2024[status]
    deduction = max(std_deduction, itemized_deductions)
    taxable_income = max(0.0, income - deduction)

    tax_owed = _marginal_tax(taxable_income, TAX_BRACKETS_2024[status])
    effective_rate = (tax_owed / income * 100) if income > 0 else 0
    balance = tax_owed - federal_withheld   # positive = owe, negative = refund

    return {
        "gross_income": income,
        "deduction_type": "itemized" if itemized_deductions > std_deduction else "standard",
        "deduction_amount": deduction,
        "taxable_income": taxable_income,
        "tax_owed": round(tax_owed, 2),
        "federal_withheld": federal_withheld,
        "effective_rate": round(effective_rate, 2),
        "amount_due": round(max(0, balance), 2),
        "refund": round(max(0, -balance), 2),
        "brackets": _bracket_breakdown(taxable_income, TAX_BRACKETS_2024[status]),
    }

def _marginal_tax(income: float, brackets: list) -> float:
    tax = 0.0
    prev = 0.0
    for cap, rate in brackets:
        if income <= prev:
            break
        taxable_in_bracket = min(income, cap) - prev
        tax += taxable_in_bracket * rate
        prev = cap
    return tax

def _bracket_breakdown(income: float, brackets: list) -> list:
    result = []
    prev = 0.0
    for cap, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, cap) - prev
        result.append({
            "rate": f"{int(rate*100)}%",
            "amount": round(taxable * rate, 2),
            "income_range": f"${int(prev):,} – {'∞' if cap == float('inf') else f'${int(cap):,}'}",
        })
        prev = cap
    return result
