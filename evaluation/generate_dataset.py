"""Evaluation dataset for the HR Ticket Classifier Agent.

This JSONL file contains test cases with expected classifications.
Each line is a JSON object with query (ticket), context, response (expected), and ground_truth.
"""

import json
from pathlib import Path

EVAL_DATASET = [
    {
        "query": "Subject: Krankmeldung\nDescription: Guten Tag, ich bin seit Montag krank und kann nicht zur Arbeit kommen. Mein Arzt hat mir ein Zeugnis ausgestellt. Voraussichtlich bin ich bis Freitag abwesend.\nCaller: Anna Müller",
        "context": "HR ticket classification for sick leave with medical certificate attached.",
        "ground_truth": json.dumps({
            "category": "Absence Management",
            "subcategory": "Sick Leave",
            "operatorGroup": "OG-HR-ABS-001",
            "language": "DE",
            "missingInfo": [],
            "confidence_min": 0.85
        }),
    },
    {
        "query": "Subject: Changement d'adresse\nDescription: Bonjour, je viens de déménager. Ma nouvelle adresse est: Rue du Marché 15, 1204 Genève. Le déménagement a eu lieu le 1er mars.\nCaller: Pierre Dupont",
        "context": "HR ticket for address change with complete information.",
        "ground_truth": json.dumps({
            "category": "Personnel Administration",
            "subcategory": "Address Change",
            "operatorGroup": "OG-HR-PA-002",
            "language": "FR",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: Payslip question\nDescription: Hi, I noticed my March payslip shows a deduction of CHF 450 under 'Other deductions' that I don't understand. Could someone explain?\nCaller: James Wilson",
        "context": "HR ticket about salary question with specific pay period identified.",
        "ground_truth": json.dumps({
            "category": "Payroll & Compensation",
            "subcategory": "Salary Question",
            "operatorGroup": "OG-HR-PAY-003",
            "language": "EN",
            "missingInfo": [],
            "confidence_min": 0.85
        }),
    },
    {
        "query": "Subject: Mutterschaftsurlaub\nDescription: Ich bin schwanger und möchte meinen Mutterschaftsurlaub planen. Errechneter Termin: 15. Juli. Ärztliches Attest reiche ich nächste Woche nach.\nCaller: Sarah Keller",
        "context": "Maternity leave planning, medical confirmation pending.",
        "ground_truth": json.dumps({
            "category": "Absence Management",
            "subcategory": "Maternity/Paternity Leave",
            "operatorGroup": "OG-HR-ABS-001",
            "language": "DE",
            "missingInfo": ["Doctor's confirmation letter"],
            "confidence_min": 0.85
        }),
    },
    {
        "query": "Subject: Signalement harcèlement\nDescription: Je souhaite signaler un comportement inapproprié d'un collègue. Depuis plusieurs semaines, cette personne fait des remarques déplacées.\nCaller: Marie Leclerc",
        "context": "Harassment report, sensitive case requiring immediate escalation.",
        "ground_truth": json.dumps({
            "category": "Workplace & Compliance",
            "subcategory": "Harassment/Discrimination Report",
            "operatorGroup": "OG-HR-COMP-009",
            "language": "FR",
            "missingInfo": [],
            "confidence_min": 0.85
        }),
    },
    {
        "query": "Subject: Cambio IBAN\nDescription: Buongiorno, ho cambiato banca. Nuovo IBAN: CH93 0076 2011 6238 5295 7. Banca: UBS. Titolare: io stesso.\nCaller: Marco Rossi",
        "context": "Bank detail change with complete IBAN information.",
        "ground_truth": json.dumps({
            "category": "Personnel Administration",
            "subcategory": "Bank Details Change",
            "operatorGroup": "OG-HR-PAY-003",
            "language": "IT",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: PRINCE2 Kurs\nDescription: Ich möchte am PRINCE2 Foundation Kurs bei Digicomp teilnehmen (10.-12. April, CHF 2400). Vorgesetzter hat mündlich zugestimmt.\nCaller: Thomas Weber",
        "context": "Training request with verbal-only manager approval.",
        "ground_truth": json.dumps({
            "category": "Training & Development",
            "subcategory": "Training Request",
            "operatorGroup": "OG-HR-LD-008",
            "language": "DE",
            "missingInfo": ["Written manager approval"],
            "confidence_min": 0.85
        }),
    },
    {
        "query": "Subject: Krank\nDescription: Hallo, ich fühle mich seit gestern nicht gut und bleibe diese Woche zu Hause. Ich weiss noch nicht wann ich zurückkomme.\nCaller: Lisa Brunner",
        "context": "Sick leave without medical certificate and no return date.",
        "ground_truth": json.dumps({
            "category": "Absence Management",
            "subcategory": "Sick Leave",
            "operatorGroup": "OG-HR-ABS-001",
            "language": "DE",
            "missingInfo": ["Medical certificate (if absence exceeds 3 days)", "Expected return date"],
            "confidence_min": 0.75
        }),
    },
    {
        "query": "Subject: Allocations familiales\nDescription: Ma femme a accouché le 5 février. Notre fils Lucas. Je demande les allocations familiales. Acte de naissance ci-joint.\nCaller: Jean-Marc Favre",
        "context": "Family allowance request with birth certificate attached.",
        "ground_truth": json.dumps({
            "category": "Benefits & Insurance",
            "subcategory": "Family Allowance",
            "operatorGroup": "OG-HR-BEN-004",
            "language": "FR",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: Vertragsfrage\nDescription: Hallo, ich habe eine Frage zu meinem Vertrag. Können Sie mich bitte zurückrufen?\nCaller: Michael Schmidt",
        "context": "Ambiguous contract question with no specifics provided.",
        "ground_truth": json.dumps({
            "category": "Employment Lifecycle",
            "subcategory": "Contract Question",
            "operatorGroup": "OG-HR-PA-002",
            "language": "DE",
            "missingInfo": ["Specific contract clause or topic of inquiry"],
            "confidence_min": 0.40
        }),
    },
    {
        "query": "Subject: Reisekosten München\nDescription: Geschäftsreise München letzte Woche. Hotel CHF 180/Nacht (2 Nächte), Zug CHF 95. Belege beigefügt.\nCaller: Sandra Huber",
        "context": "Expense reimbursement with itemized costs and receipts.",
        "ground_truth": json.dumps({
            "category": "Payroll & Compensation",
            "subcategory": "Expense Reimbursement",
            "operatorGroup": "OG-HR-PAY-003",
            "language": "DE",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: Work Reference Letter\nDescription: I am applying for a new position externally and need a work reference letter in English. 4 years in Marketing department.\nCaller: David Chen",
        "context": "Reference letter request with clear purpose and language preference.",
        "ground_truth": json.dumps({
            "category": "Employment Lifecycle",
            "subcategory": "Reference Letter Request",
            "operatorGroup": "OG-HR-PA-002",
            "language": "EN",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: Kündigung\nDescription: Hiermit kündige ich mein Arbeitsverhältnis per 30. Juni. Mein Kündigungsschreiben ist beigefügt.\nCaller: Peter Meier",
        "context": "Resignation with written letter attached and clear last day.",
        "ground_truth": json.dumps({
            "category": "Employment Lifecycle",
            "subcategory": "Resignation",
            "operatorGroup": "OG-HR-OFF-006",
            "language": "DE",
            "missingInfo": [],
            "confidence_min": 0.95
        }),
    },
    {
        "query": "Subject: Pensionsfrage\nDescription: Ich werde in 2 Jahren pensioniert und möchte wissen wie hoch meine voraussichtliche Rente sein wird. Können Sie mir eine Berechnung zukommen lassen?\nCaller: Hans Zimmermann",
        "context": "Pension query with retirement timeline.",
        "ground_truth": json.dumps({
            "category": "Benefits & Insurance",
            "subcategory": "Pension/Retirement Query",
            "operatorGroup": "OG-HR-BEN-004",
            "language": "DE",
            "missingInfo": [],
            "confidence_min": 0.90
        }),
    },
    {
        "query": "Subject: Homeoffice Anfrage\nDescription: Ich möchte ab nächstem Monat 2 Tage pro Woche von zu Hause arbeiten. Mein Vorgesetzter ist einverstanden. Ist das möglich?\nCaller: Julia Fischer",
        "context": "Work from home request with manager agreement mentioned.",
        "ground_truth": json.dumps({
            "category": "Workplace & Compliance",
            "subcategory": "Work-from-Home Request",
            "operatorGroup": "OG-HR-PA-002",
            "language": "DE",
            "missingInfo": ["Proposed WFH schedule details", "Duration (temporary/permanent)"],
            "confidence_min": 0.80
        }),
    },
]


def generate_eval_dataset():
    """Write evaluation dataset to JSONL file."""
    output_path = Path(__file__).parent / "eval_dataset.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for item in EVAL_DATASET:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Generated evaluation dataset: {output_path} ({len(EVAL_DATASET)} test cases)")
    return output_path


if __name__ == "__main__":
    generate_eval_dataset()
