# Operator Group Mappings

| Operator Group Name | TOPdesk ID | Description |
|---|---|---|
| HR-Absence-Management | OG-HR-ABS-001 | Handles all leave types: sick, vacation, maternity, unpaid, bereavement |
| HR-Personnel-Admin | OG-HR-PA-002 | Personal data changes, contracts, references, work arrangements |
| HR-Payroll | OG-HR-PAY-003 | Salary questions, expenses, tax certificates, bank details |
| HR-Benefits | OG-HR-BEN-004 | Insurance, pension, family allowances, claims |
| HR-Onboarding | OG-HR-ONB-005 | New hire questions, first-day logistics, documentation |
| HR-Offboarding | OG-HR-OFF-006 | Resignations, exit procedures, final settlements |
| HR-Talent-Management | OG-HR-TM-007 | Performance reviews, internal transfers, career development |
| HR-Learning-Development | OG-HR-LD-008 | Training requests, education reimbursement, certifications |
| HR-Compliance | OG-HR-COMP-009 | Harassment reports, whistleblower cases, policy violations |

## Routing Rules

1. **Default escalation**: If no clear category match, route to `HR-Personnel-Admin`
2. **High priority**: Compliance tickets (harassment, whistleblower) always route to `HR-Compliance`
3. **Payroll overlap**: Bank detail changes go to `HR-Payroll`, not `HR-Personnel-Admin`
4. **Leave overlap**: All leave types (including unpaid) go to `HR-Absence-Management`
5. **Multi-category tickets**: Route to the primary category's group; mention secondary in notes
