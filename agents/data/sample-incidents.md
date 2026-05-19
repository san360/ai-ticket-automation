# Sample Incidents — Few-Shot Classification Examples

## Example 1: Sick Leave (German)

**Ticket Text:**
> Guten Tag, ich bin seit Montag krank und kann nicht zur Arbeit kommen. Mein Arzt hat mir ein Zeugnis ausgestellt, das ich hier anhänge. Voraussichtlich bin ich bis Freitag abwesend.

**Classification:**
```json
{
  "category": "Absence Management",
  "subcategory": "Sick Leave",
  "operatorGroup": "OG-HR-ABS-001",
  "language": "DE",
  "missingInfo": [],
  "confidence": 0.95,
  "confidenceReasoning": "Clear sick leave report with medical certificate attached and expected return date provided."
}
```

---

## Example 2: Address Change (French)

**Ticket Text:**
> Bonjour, je viens de déménager et j'aimerais mettre à jour mon adresse. Ma nouvelle adresse est: Rue du Marché 15, 1204 Genève. Le déménagement a eu lieu le 1er mars.

**Classification:**
```json
{
  "category": "Personnel Administration",
  "subcategory": "Address Change",
  "operatorGroup": "OG-HR-PA-002",
  "language": "FR",
  "missingInfo": [],
  "confidence": 0.98,
  "confidenceReasoning": "Explicit address change request with complete new address and move date."
}
```

---

## Example 3: Sick Leave Missing Certificate (German)

**Ticket Text:**
> Hallo, ich fühle mich seit gestern nicht gut und bleibe diese Woche zu Hause. Ich weiss noch nicht wann ich zurückkomme.

**Classification:**
```json
{
  "category": "Absence Management",
  "subcategory": "Sick Leave",
  "operatorGroup": "OG-HR-ABS-001",
  "language": "DE",
  "missingInfo": ["Medical certificate (required if absence exceeds 3 days)", "Expected return date"],
  "confidence": 0.85,
  "confidenceReasoning": "Clear sick leave indication but no medical certificate and no return date. Duration unclear - may exceed 3-day threshold."
}
```

---

## Example 4: Salary Question (English)

**Ticket Text:**
> Hi, I noticed my March payslip shows a deduction of CHF 450 under "Other deductions" that I don't understand. Could someone explain what this is for?

**Classification:**
```json
{
  "category": "Payroll & Compensation",
  "subcategory": "Salary Question",
  "operatorGroup": "OG-HR-PAY-003",
  "language": "EN",
  "missingInfo": [],
  "confidence": 0.95,
  "confidenceReasoning": "Clear salary/payslip question with specific pay period (March) and line item identified."
}
```

---

## Example 5: Maternity Leave (German)

**Ticket Text:**
> Liebe HR, ich bin schwanger und möchte meinen Mutterschaftsurlaub planen. Der errechnete Termin ist am 15. Juli. Ich möchte 2 Wochen vor dem Termin in den Urlaub gehen. Das ärztliche Attest reiche ich nächste Woche nach.

**Classification:**
```json
{
  "category": "Absence Management",
  "subcategory": "Maternity/Paternity Leave",
  "operatorGroup": "OG-HR-ABS-001",
  "language": "DE",
  "missingInfo": ["Doctor's confirmation letter (to be submitted next week)"],
  "confidence": 0.92,
  "confidenceReasoning": "Clear maternity leave request with expected date and desired start. Medical confirmation acknowledged but not yet provided."
}
```

---

## Example 6: Harassment Report (French)

**Ticket Text:**
> Je souhaite signaler un comportement inapproprié de la part d'un collègue. Depuis plusieurs semaines, cette personne fait des remarques déplacées à mon égard. Je préfère ne pas donner les détails ici mais j'aimerais en parler à quelqu'un de confiance.

**Classification:**
```json
{
  "category": "Workplace & Compliance",
  "subcategory": "Harassment/Discrimination Report",
  "operatorGroup": "OG-HR-COMP-009",
  "language": "FR",
  "missingInfo": [],
  "confidence": 0.90,
  "confidenceReasoning": "Clear harassment report. Employee prefers verbal disclosure of details - this is appropriate for sensitive cases. No missing info as initial report is sufficient to trigger confidential follow-up."
}
```

---

## Example 7: Bank Details Change (Italian)

**Ticket Text:**
> Buongiorno, ho cambiato banca e vorrei aggiornare i miei dati bancari per il versamento dello stipendio. Il nuovo IBAN è CH93 0076 2011 6238 5295 7. La banca è UBS. Il titolare del conto sono io.

**Classification:**
```json
{
  "category": "Personnel Administration",
  "subcategory": "Bank Details Change",
  "operatorGroup": "OG-HR-PAY-003",
  "language": "IT",
  "missingInfo": [],
  "confidence": 0.97,
  "confidenceReasoning": "Explicit bank detail change with complete IBAN, bank name, and account holder confirmation. Note: routes to Payroll per routing rules."
}
```

---

## Example 8: Training Request (German)

**Ticket Text:**
> Hallo HR-Team, ich möchte gerne an einem Projektmanagement-Kurs teilnehmen. Es handelt sich um den "PRINCE2 Foundation" Kurs bei Digicomp vom 10.-12. April. Die Kosten betragen CHF 2'400. Mein Vorgesetzter hat mündlich zugestimmt.

**Classification:**
```json
{
  "category": "Training & Development",
  "subcategory": "Training Request",
  "operatorGroup": "OG-HR-LD-008",
  "language": "DE",
  "missingInfo": ["Written manager approval (only verbal approval mentioned)"],
  "confidence": 0.93,
  "confidenceReasoning": "Clear training request with course name, provider, dates, and cost. Manager approval is verbal only - written confirmation needed."
}
```

---

## Example 9: Ambiguous Ticket (German)

**Ticket Text:**
> Hallo, ich habe eine Frage zu meinem Vertrag. Können Sie mich bitte zurückrufen?

**Classification:**
```json
{
  "category": "Employment Lifecycle",
  "subcategory": "Contract Question",
  "operatorGroup": "OG-HR-PA-002",
  "language": "DE",
  "missingInfo": ["Specific contract clause or topic of inquiry"],
  "confidence": 0.55,
  "confidenceReasoning": "Employee mentions 'contract question' but provides no specifics. Could potentially relate to other categories depending on the actual question. Low confidence due to minimal context."
}
```

---

## Example 10: Family Allowance (French)

**Ticket Text:**
> Bonjour, ma femme vient d'accoucher le 5 février. Notre fils s'appelle Lucas. Je voudrais demander les allocations familiales. Ci-joint l'acte de naissance.

**Classification:**
```json
{
  "category": "Benefits & Insurance",
  "subcategory": "Family Allowance",
  "operatorGroup": "OG-HR-BEN-004",
  "language": "FR",
  "missingInfo": [],
  "confidence": 0.97,
  "confidenceReasoning": "Clear family allowance request for new child with birth date, child's name, and birth certificate attached."
}
```

---

## Example 11: Reference Letter (English)

**Ticket Text:**
> Hello, I am applying for a new position externally and would need a work reference letter. Could you please prepare one in English? I have been with the company for 4 years in the Marketing department.

**Classification:**
```json
{
  "category": "Employment Lifecycle",
  "subcategory": "Reference Letter Request",
  "operatorGroup": "OG-HR-PA-002",
  "language": "EN",
  "missingInfo": [],
  "confidence": 0.96,
  "confidenceReasoning": "Clear reference letter request with purpose (external application), preferred language (English), and context (4 years, Marketing)."
}
```

---

## Example 12: Expense Reimbursement (German)

**Ticket Text:**
> Guten Tag, ich war letzte Woche auf Geschäftsreise in München und möchte meine Reisekosten abrechnen. Hotel: CHF 180/Nacht (2 Nächte), Zugticket: CHF 95. Die Belege sind beigefügt.

**Classification:**
```json
{
  "category": "Payroll & Compensation",
  "subcategory": "Expense Reimbursement",
  "operatorGroup": "OG-HR-PAY-003",
  "language": "DE",
  "missingInfo": [],
  "confidence": 0.96,
  "confidenceReasoning": "Clear expense reimbursement with itemized costs, business justification (business trip), and receipts attached."
}
```
