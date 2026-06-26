"""
SentinelX Realtime Call Analyzer
=================================
Processes a call turn-by-turn, showing escalating risk live.

Usage:
    python realtime_analyzer.py
"""

import warnings
warnings.filterwarnings("ignore")

from pipeline import SentinelXIndex, score_risk, INDEX_DIR

def analyze_call(turns: list[str], verbose=True) -> list[dict]:
    index = SentinelXIndex.load(INDEX_DIR)
    results, cumulative = [], ""

    if verbose:
        print("=" * 62)
        print("  SentinelX — Live Call Risk Analyzer")
        print("=" * 62)
        print()

    for i, turn in enumerate(turns, 1):
        cumulative += (" | " if cumulative else "") + turn
        r   = score_risk(index, cumulative)
        risk = r["risk_score"]
        filled = int(risk * 20)
        bar  = "█" * filled + "░" * (20 - filled)

        if verbose:
            color = "\033[91m" if r["verdict"] == "SCAM" else \
                    "\033[93m" if r["verdict"] == "SUSPICIOUS" else "\033[92m"
            reset = "\033[0m"
            print(f"  Turn {i} │ {color}[{bar}]{reset} {risk:.3f} │ {r['verdict']:10} │ {r['matched_category']}")
            print(f"         └─ {turn[:80]}")
            print()

        results.append({"turn": i, "text": turn, **r})

    if verbose:
        final = results[-1]
        print("─" * 62)
        print(f"  Final verdict : {final['verdict']}")
        print(f"  Risk score    : {final['risk_score']}")
        print(f"  Category      : {final['matched_category']}")
        print("─" * 62)

    return results


if __name__ == "__main__":
    # ── Demo 1: Bank Impersonation (Hinglish) ──
    print("\n【 Demo 1 — Bank Impersonation (Hinglish) 】\n")
    analyze_call([
        "Namaste, main SBI Bank customer care se bol raha hoon.",
        "Aapke account mein suspicious activity detect hui hai.",
        "Verification ke liye Aadhaar number aur date of birth chahiye.",
        "Ek OTP aayega — woh share karein toh account restore ho jayega.",
        "OTP confirm ho gaya. Account suspend hone se bach gaya.",
    ])

    # ── Demo 2: Legitimate delivery call (Tenglish) ──
    print("\n【 Demo 2 — Legitimate Delivery (Tenglish) 】\n")
    analyze_call([
        "Namaskaram, nenu Swiggy delivery executive ni.",
        "Meeru order ready ga undi, building gate daggera unnaanu.",
        "Security vaalllu lopalaiki ranivatle ledu — meeru ravagalara?",
        "Vachhaaru! OTP 4782 confirm chesaamu. Enjoy cheyyandi!",
    ])

    # ── Demo 3: Lottery Scam (English) ──
    print("\n【 Demo 3 — Lottery Scam (English) 】\n")
    analyze_call([
        "Congratulations! You have won the KBC lucky draw.",
        "Your prize amount is Rs 25 lakh — selected from 5 crore subscribers.",
        "To release the prize, a processing fee of Rs 5,000 must be paid.",
        "Pay to account number given and prize will transfer within 24 hours.",
    ])
