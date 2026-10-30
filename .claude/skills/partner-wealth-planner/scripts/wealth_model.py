"""Long-term wealth model for comparing partner offers.

Year-by-year, nominal, pre-tax. Each modeled year runs from one birthday to the
next. Partner earnings and any pension flow into a holding company or trust,
a fixed salary is drawn out, and the remainder compounds at a single rate.

    balance[end] = balance[start] * (1 + r) + earnings + pension - salary

Earnings and pension are credited at year end, so a year's inflows start
earning the following year. That's the conservative convention.

Usage:
    python wealth_model.py config.json [--xlsx out.xlsx]
"""

import argparse
import json


def annuity_payment(pv, rate, years):
    """Level end-of-year payment that draws pv to zero over `years`."""
    if years <= 0:
        return 0.0
    if rate == 0:
        return pv / years
    return pv * rate / (1 - (1 + rate) ** -years)


def earnings_for_year(scn, years_from_now):
    """Partner earnings in a working year, grown from today's level."""
    if "units" in scn:
        base = scn["units"] * scn["unit_value"]
    else:
        base = scn["base_earnings"]
    return base * (1 + scn["earnings_growth"]) ** years_from_now


def pension_at_retirement(scn, a):
    """Annual pension in the first year it is paid."""
    p = scn["pension"]
    if p.get("grows_until_retirement"):
        years = scn["retirement_age"] - a["current_age"]
        return p["annual"] * (1 + p["pre_retirement_growth"]) ** years
    return p["annual"]


def run_scenario(scn, a):
    r = a["return_rate"]
    salary = a["monthly_salary"] * 12
    start_pension = pension_at_retirement(scn, a)
    cola = scn["pension"].get("cola", 0.0)

    rows = []
    balance = a.get("opening_balance", 0.0)
    for age in range(a["current_age"], a["life_expectancy"] + 1):
        t = age - a["current_age"]
        working = age < scn["retirement_age"]
        earnings = earnings_for_year(scn, t) if working else 0.0
        if working:
            pension = 0.0
        else:
            pension = start_pension * (1 + cola) ** (age - scn["retirement_age"])
        growth = balance * r
        net_invested = earnings + pension - salary
        opening = balance
        balance = opening + growth + net_invested
        rows.append({
            "age": age,
            "status": "Working" if working else "Retired",
            "opening_balance": opening,
            "earnings": earnings,
            "pension": pension,
            "salary": salary,
            "investment_growth": growth,
            "net_invested": net_invested,
            "closing_balance": balance,
        })
    return rows, start_pension


def summarize(name, scn, a, rows, start_pension):
    snap_age = a["snapshot_age"]
    upto = [x for x in rows if x["age"] < snap_age]
    after = [x for x in rows if x["age"] >= snap_age]
    bal_at_snap = upto[-1]["closing_balance"]
    r = a["return_rate"]
    years_left = a["life_expectancy"] - snap_age + 1

    pension_rows = [x for x in rows if x["pension"] > 0]
    pension_at_snap = after[0]["pension"] if after else 0.0
    return {
        "name": name,
        "retirement_age": scn["retirement_age"],
        "pension_start": start_pension,
        "earnings_to_snap": sum(x["earnings"] for x in upto),
        "salary_to_snap": sum(x["salary"] for x in upto),
        "pension_to_snap": sum(x["pension"] for x in upto),
        "growth_to_snap": sum(x["investment_growth"] for x in upto),
        "balance_at_snap": bal_at_snap,
        "pension_lifetime": sum(x["pension"] for x in pension_rows),
        "pension_years": len(pension_rows),
        "pension_at_snap": pension_at_snap,
        "investment_income_at_snap": bal_at_snap * r,
        "drawdown_to_life_exp": annuity_payment(bal_at_snap, r, years_left),
        "balance_at_end": rows[-1]["closing_balance"],
    }


def fmt(x):
    return f"${x:,.0f}"


def print_report(summaries, a):
    s = a["snapshot_age"]
    lines = [
        ("Retirement age", lambda x: str(x["retirement_age"])),
        ("Partner earnings, now to " + str(s), lambda x: fmt(x["earnings_to_snap"])),
        ("Salary drawn, now to " + str(s), lambda x: fmt(x["salary_to_snap"])),
        ("Pension received before " + str(s), lambda x: fmt(x["pension_to_snap"])),
        ("Investment growth, now to " + str(s), lambda x: fmt(x["growth_to_snap"])),
        ("Portfolio at " + str(s), lambda x: fmt(x["balance_at_snap"])),
        ("Salary + pension + portfolio at " + str(s),
         lambda x: fmt(x["salary_to_snap"] + x["pension_to_snap"] + x["balance_at_snap"])),
        ("Annual pension, first year", lambda x: fmt(x["pension_start"])),
        ("Lifetime pension to " + str(a["life_expectancy"]),
         lambda x: f"{fmt(x['pension_lifetime'])} ({x['pension_years']} yrs)"),
        ("Pension per year from " + str(s), lambda x: fmt(x["pension_at_snap"])),
        ("Investment income at 5% from " + str(s), lambda x: fmt(x["investment_income_at_snap"])),
        ("Income from " + str(s) + ", capital intact",
         lambda x: fmt(x["pension_at_snap"] + x["investment_income_at_snap"])),
        ("Income from " + str(s) + ", draw to $0 by " + str(a["life_expectancy"]),
         lambda x: fmt(x["pension_at_snap"] + x["drawdown_to_life_exp"])),
        ("Portfolio at " + str(a["life_expectancy"]) + " (keep $" +
         f"{a['monthly_salary'] * 12:,.0f}" + " draw)", lambda x: fmt(x["balance_at_end"])),
    ]
    w = max(len(label) for label, _ in lines) + 2
    header = "".ljust(w) + "".join(x["name"].rjust(26) for x in summaries)
    print(header)
    print("-" * len(header))
    for label, f in lines:
        print(label.ljust(w) + "".join(f(x).rjust(26) for x in summaries))


def write_xlsx(path, results, summaries, a):
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Metric"] + [x["name"] for x in summaries])
    keys = [
        ("Retirement age", "retirement_age"),
        ("Partner earnings to snapshot", "earnings_to_snap"),
        ("Salary drawn to snapshot", "salary_to_snap"),
        ("Pension received before snapshot", "pension_to_snap"),
        ("Investment growth to snapshot", "growth_to_snap"),
        ("Portfolio at snapshot", "balance_at_snap"),
        ("Annual pension, first year", "pension_start"),
        ("Lifetime pension", "pension_lifetime"),
        ("Pension per year at snapshot", "pension_at_snap"),
        ("Investment income at snapshot", "investment_income_at_snap"),
        ("Level drawdown to life expectancy", "drawdown_to_life_exp"),
        ("Portfolio at life expectancy", "balance_at_end"),
    ]
    for label, k in keys:
        ws.append([label] + [x[k] for x in summaries])
    for row in ws.iter_rows(min_row=2, min_col=2):
        for c in row:
            c.number_format = "$#,##0"
    ws.append([])
    ws.append(["Assumptions"])
    for k, v in a.items():
        ws.append([k, v])
    ws.column_dimensions["A"].width = 38
    for col in "BCDEFG":
        ws.column_dimensions[col].width = 22
    for c in ws[1]:
        c.font = Font(bold=True)

    cols = ["age", "status", "opening_balance", "earnings", "pension", "salary",
            "investment_growth", "net_invested", "closing_balance"]
    for name, rows in results:
        sh = wb.create_sheet(name[:31])
        sh.append([c.replace("_", " ").title() for c in cols])
        for c in sh[1]:
            c.font = Font(bold=True)
        for x in rows:
            sh.append([x[c] for c in cols])
        for row in sh.iter_rows(min_row=2, min_col=3):
            for c in row:
                c.number_format = "$#,##0;($#,##0)"
        for i in range(len(cols)):
            sh.column_dimensions[chr(65 + i)].width = 18
    wb.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--xlsx")
    args = ap.parse_args()
    with open(args.config) as f:
        cfg = json.load(f)
    a = cfg["assumptions"]

    results, summaries = [], []
    for name, scn in cfg["scenarios"].items():
        rows, start_pension = run_scenario(scn, a)
        results.append((name, rows))
        summaries.append(summarize(name, scn, a, rows, start_pension))

    print_report(summaries, a)
    if args.xlsx:
        write_xlsx(args.xlsx, results, summaries, a)
        print(f"\nWorkbook written to {args.xlsx}")


if __name__ == "__main__":
    main()
