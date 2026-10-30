"""Pension later vs cash now: which stream is worth more?

Option A, pension: `pension` a year from `pension_start` to `life`, rising by
`cola` each year once paid.
Option B, cash: `cash` a year from `cash_start` to `cash_end`, invested.

Both streams are valued the same way: every payment is invested at the
return `r` the moment it arrives (end of year), so the comparison is
- present value today, and
- portfolio value at `life` if everything is reinvested.
Option B is also turned into the level income it could fund over the
pension years, so it reads in the same units as the pension.

Usage:
    python pension_vs_cash.py --age 50 --pension 150000 --pension-start 60 \
        --cash 150000 --cash-start 51 --cash-end 60 --life 90
"""

import argparse


def stream(amount, start, end, growth=0.0):
    return [(age, amount * (1 + growth) ** (age - start)) for age in range(start, end + 1)]


def pv(flows, r, age0):
    return sum(c / (1 + r) ** (age - age0) for age, c in flows)


def breakeven(a_flows, b_flows, age0, lo=-0.05, hi=0.30):
    """Return at which both streams have equal present value."""
    f = lambda r: pv(a_flows, r, age0) - pv(b_flows, r, age0)
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def compare(args, r, life=None, cola=None):
    life = life or args.life
    cola = args.cola if cola is None else cola
    a = stream(args.pension, args.pension_start, life, cola)
    b = stream(args.cash, args.cash_start, args.cash_end)
    pv_a, pv_b = pv(a, r, args.age), pv(b, r, args.age)
    fv = (1 + r) ** (life - args.age)
    # level income over the pension years that B's value could fund
    annuity = pv(stream(1, args.pension_start, life, cola), r, args.age)
    return {
        "pv_a": pv_a, "pv_b": pv_b,
        "fv_a": pv_a * fv, "fv_b": pv_b * fv,
        "b_as_pension": pv_b / annuity,
        "total_a": sum(c for _, c in a), "total_b": sum(c for _, c in b),
        "be": breakeven(a, b, args.age),
    }


def m(v):
    return f"${v/1e6:,.2f}M" if abs(v) >= 1e6 else f"${v/1e3:,.0f}k"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--age", type=int, required=True)
    ap.add_argument("--pension", type=float, required=True)
    ap.add_argument("--pension-start", type=int, required=True)
    ap.add_argument("--cola", type=float, default=0.0)
    ap.add_argument("--cash", type=float, required=True)
    ap.add_argument("--cash-start", type=int, required=True)
    ap.add_argument("--cash-end", type=int, required=True)
    ap.add_argument("--life", type=int, default=90)
    ap.add_argument("--rates", type=float, nargs="+", default=[0.06, 0.07, 0.08, 0.09, 0.10])
    args = ap.parse_args()

    base = compare(args, args.rates[0])
    print(f"A pension: {m(args.pension)}/yr, ages {args.pension_start}-{args.life}, "
          f"COLA {args.cola:.1%}, total {m(base['total_a'])}")
    print(f"B cash:    {m(args.cash)}/yr, ages {args.cash_start}-{args.cash_end}, "
          f"total {m(base['total_b'])}\n")

    hdr = f"{'Return':>7}{'PV A':>11}{'PV B':>11}{'A at ' + str(args.life):>12}{'B at ' + str(args.life):>12}{'B as pension':>14}  Better"
    print(hdr)
    print("-" * len(hdr))
    for r in args.rates:
        c = compare(args, r)
        win = "Cash" if c["pv_b"] > c["pv_a"] else "Pension"
        print(f"{r:>7.1%}{m(c['pv_a']):>11}{m(c['pv_b']):>11}{m(c['fv_a']):>12}{m(c['fv_b']):>12}"
              f"{m(c['b_as_pension']) + '/yr':>14}  {win}")

    print(f"\nBreak-even return: {base['be']:.2%} (cash wins above it, pension below)")
    print("\nBreak-even return by age at death:")
    for life in (75, 80, 85, 90, 95):
        print(f"  {life}: {compare(args, 0.07, life=life)['be']:.2%}")
    print("\nBreak-even return by pension indexing:")
    for cola in (0.0, 0.01, 0.02, 0.03):
        print(f"  COLA {cola:.0%}: {compare(args, 0.07, cola=cola)['be']:.2%}")


if __name__ == "__main__":
    main()
