"""Generate the synthetic policy corpus and the eval questions with gold sources.

Every document shares the same section layout, so retrieval has to tell
look-alike clauses apart by product name and numbers, as it would on real
policy wordings. Run: python corpus/generate.py
"""
import json
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).parent
PDF_DIR = ROOT / "pdfs"
QUESTIONS = ROOT.parent / "eval" / "questions.json"

SECTIONS = [
    "Definitions", "Coverage", "Exclusions", "Waiting Periods",
    "Claims Procedure", "Premiums and Grace Period", "Cancellation and Free Look",
]

POLICIES = [
    dict(id="shieldcare-health", name="ShieldCare Health Plus", kind="health", sum=500000,
         ded=1000, wait=30, claim=45, cancel=30, free=15, prem=420, grace=30,
         special="maternity care up to $15,000 after a 24-month wait",
         excl="cosmetic surgery and dental whitening"),
    dict(id="roadsafe-auto", name="RoadSafe Comprehensive Auto", kind="auto", sum=75000,
         ded=500, wait=0, claim=30, cancel=14, free=10, prem=96, grace=15,
         special="roadside assistance with towing up to 50 miles",
         excl="racing, track days and commercial delivery use"),
    dict(id="homeguard-home", name="HomeGuard Property Cover", kind="home", sum=350000,
         ded=1500, wait=7, claim=60, cancel=30, free=14, prem=58, grace=30,
         special="alternative accommodation for up to 12 months after a covered fire",
         excl="flood damage unless the Flood Extension is purchased"),
    dict(id="globetrek-travel", name="GlobeTrek Travel Protect", kind="travel", sum=100000,
         ded=100, wait=2, claim=21, cancel=7, free=7, prem=45, grace=5,
         special="emergency medical evacuation with no sub-limit",
         excl="travel against government advisories and extreme sports"),
    dict(id="lifebridge-term", name="LifeBridge Term Life 20", kind="life", sum=1000000,
         ded=0, wait=365, claim=90, cancel=60, free=30, prem=38, grace=31,
         special="accelerated death benefit of 25% on terminal illness diagnosis",
         excl="suicide within the first 24 months"),
    dict(id="rentsafe-renters", name="RentSafe Renters Cover", kind="renters", sum=40000,
         ded=250, wait=3, claim=30, cancel=15, free=10, prem=14, grace=15,
         special="personal liability cover of $100,000 per occurrence",
         excl="roommates' belongings unless named on the schedule"),
    dict(id="pawsure-pet", name="PawSure Pet Care", kind="pet", sum=15000,
         ded=200, wait=14, claim=60, cancel=30, free=14, prem=32, grace=30,
         special="hereditary conditions covered after a 12-month wait",
         excl="pre-existing conditions and breeding costs"),
    dict(id="criticalcover-ci", name="CriticalCover Illness Benefit", kind="critical illness",
         sum=250000, ded=0, wait=90, claim=60, cancel=30, free=30, prem=64, grace=30,
         special="a lump sum on diagnosis of any of 36 listed conditions",
         excl="conditions diagnosed within the 90-day waiting period"),
    dict(id="cyberarmor-cyber", name="CyberArmor Small Business", kind="cyber", sum=500000,
         ded=2500, wait=0, claim=14, cancel=30, free=10, prem=110, grace=30,
         special="ransomware negotiation and recovery costs",
         excl="losses from unpatched systems older than 90 days"),
    dict(id="buildright-commercial", name="BuildRight Commercial Property", kind="commercial",
         sum=2000000, ded=5000, wait=14, claim=45, cancel=60, free=15, prem=310, grace=30,
         special="business interruption cover for up to 18 months of lost profit",
         excl="wear and tear, and vacant premises over 60 days"),
    dict(id="seniorcare-health", name="SeniorCare Medicare Supplement", kind="senior health",
         sum=300000, ded=750, wait=180, claim=60, cancel=30, free=30, prem=275, grace=31,
         special="skilled nursing facility cover for 100 days per benefit period",
         excl="long-term custodial care"),
    dict(id="umbrellaplus-liability", name="UmbrellaPlus Personal Liability", kind="umbrella",
         sum=2000000, ded=0, wait=0, claim=30, cancel=30, free=14, prem=27, grace=30,
         special="defence costs paid in addition to the policy limit",
         excl="business activities and intentional acts"),
]


def sections(p: dict) -> dict[str, list[str]]:
    n, k = p["name"], p["kind"]
    return {
        "Definitions": [
            f'"Policy" means the {n} {k} policy wording and schedule issued to you.',
            f'"Insured Amount" means ${p["sum"]:,}, the most we pay in total in any policy year.',
            f'"Deductible" means ${p["ded"]:,}, the portion of each claim you bear first.',
        ],
        "Coverage": [
            f"{n} pays covered losses up to the Insured Amount of ${p['sum']:,} per policy year.",
            f"Extra benefit: {p['special']}.",
            f"A deductible of ${p['ded']:,} applies to each separate claim.",
        ],
        "Exclusions": [
            f"{n} does not cover {p['excl']}.",
            "We do not pay for losses caused by war, nuclear risks or deliberate acts.",
            "Fraudulent or exaggerated claims void the claim and may void the policy.",
        ],
        "Waiting Periods": [
            f"Cover under {n} starts after a waiting period of {p['wait']} days from the "
            "policy start date.",
            "Claims for events during the waiting period are not payable.",
            "The waiting period does not apply to renewals without a break in cover.",
        ],
        "Claims Procedure": [
            f"Notify us of a claim under {n} within {p['claim']} days of the event.",
            "Send the claim form, proof of loss and any bills or reports we ask for.",
            "We aim to settle valid claims within 15 working days of receiving every document.",
        ],
        "Premiums and Grace Period": [
            f"The premium for {n} is ${p['prem']} per month, due on the first of each month.",
            f"A grace period of {p['grace']} days applies to late payments, and cover continues "
            "during the grace period.",
            "If the premium is still unpaid when the grace period ends, the policy lapses.",
        ],
        "Cancellation and Free Look": [
            f"You may cancel {n} within the {p['free']}-day free look period for a full refund.",
            f"After the free look period, cancelling needs {p['cancel']} days written notice.",
            "We may cancel for non-payment or fraud with 14 days written notice.",
        ],
    }


def build_pdf(p: dict) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, p["name"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "Policy wording (synthetic sample for demonstration only).")
    for i, (title, clauses) in enumerate(sections(p).items(), 1):
        if i == 4:
            pdf.add_page()
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"{i}. {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for j, clause in enumerate(clauses, 1):
            pdf.multi_cell(0, 6, f"{i}.{j} {clause}", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(PDF_DIR / f"{p['id']}.pdf"))


def questions() -> list[dict]:
    by = {p["id"]: p for p in POLICIES}
    spec = [
        ("shieldcare-health", "Waiting Periods", "How long is the waiting period for ShieldCare Health Plus?", "{wait} days"),
        ("roadsafe-auto", "Claims Procedure", "Within how many days must I report an accident to RoadSafe?", "{claim} days"),
        ("homeguard-home", "Coverage", "What deductible applies to each HomeGuard claim?", "${ded:,}"),
        ("globetrek-travel", "Premiums and Grace Period", "What monthly premium does GlobeTrek Travel Protect charge?", "${prem}"),
        ("lifebridge-term", "Cancellation and Free Look", "How long is the free look period on LifeBridge Term Life 20?", "{free} days"),
        ("rentsafe-renters", "Exclusions", "What does RentSafe Renters Cover exclude about roommates?", "roommates' belongings"),
        ("pawsure-pet", "Waiting Periods", "How many days before PawSure Pet Care cover begins?", "{wait} days"),
        ("criticalcover-ci", "Coverage", "How many conditions does CriticalCover pay a lump sum for?", "36"),
        ("cyberarmor-cyber", "Exclusions", "Does CyberArmor pay for losses from unpatched systems?", "unpatched"),
        ("buildright-commercial", "Coverage", "How long does BuildRight business interruption cover last?", "18 months"),
        ("seniorcare-health", "Coverage", "How many days of skilled nursing does SeniorCare cover?", "100 days"),
        ("umbrellaplus-liability", "Coverage", "What is the liability limit on UmbrellaPlus Personal Liability?", "${sum:,}"),
        ("shieldcare-health", "Premiums and Grace Period", "What is the grace period for late premium on ShieldCare?", "{grace} days"),
        ("roadsafe-auto", "Exclusions", "Is racing covered by RoadSafe Comprehensive Auto?", "racing"),
        ("homeguard-home", "Cancellation and Free Look", "How much notice must I give to cancel HomeGuard after free look?", "{cancel} days"),
        ("globetrek-travel", "Coverage", "Is there a sub-limit on medical evacuation under GlobeTrek?", "no sub-limit"),
        ("lifebridge-term", "Waiting Periods", "How long is the LifeBridge waiting period in days?", "{wait} days"),
        ("rentsafe-renters", "Premiums and Grace Period", "How many grace days does RentSafe allow for late payment?", "{grace} days"),
        ("pawsure-pet", "Exclusions", "Are pre-existing conditions covered by PawSure?", "not covered"),
        ("criticalcover-ci", "Claims Procedure", "When must a CriticalCover claim be notified?", "{claim} days"),
        ("cyberarmor-cyber", "Coverage", "What is the deductible on CyberArmor Small Business?", "${ded:,}"),
        ("buildright-commercial", "Exclusions", "What does BuildRight say about vacant premises?", "60 days"),
        ("seniorcare-health", "Cancellation and Free Look", "What is the free look period for SeniorCare Medicare Supplement?", "{free} days"),
        ("umbrellaplus-liability", "Exclusions", "Does UmbrellaPlus cover business activities?", "not covered"),
        ("shieldcare-health", "Coverage", "Is maternity covered under ShieldCare Health Plus?", "$15,000"),
        ("roadsafe-auto", "Coverage", "How far does RoadSafe towing go?", "50 miles"),
        ("homeguard-home", "Waiting Periods", "What is the HomeGuard waiting period before cover starts?", "{wait} days"),
        ("globetrek-travel", "Cancellation and Free Look", "What is the GlobeTrek free look period?", "{free} days"),
        ("lifebridge-term", "Coverage", "What does LifeBridge pay on terminal illness diagnosis?", "25%"),
        ("pawsure-pet", "Coverage", "When are hereditary conditions covered by PawSure?", "12-month"),
    ]
    out = []
    for i, (pid, section, q, ans) in enumerate(spec, 1):
        out.append({"id": f"q{i:02d}", "question": q, "doc": pid,
                    "section": section, "expected": ans.format(**by[pid])})
    return out


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for p in POLICIES:
        build_pdf(p)
    QUESTIONS.write_text(json.dumps(questions(), indent=2) + "\n")
    print(f"wrote {len(POLICIES)} PDFs and {len(questions())} questions")


if __name__ == "__main__":
    main()
