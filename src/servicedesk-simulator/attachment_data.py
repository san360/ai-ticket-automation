"""Synthetic attachment data for testing document analysis.

Provides simulated attachment metadata and extracted text content for tickets
that have attachments (e.g., medical certificates for sick leave).
"""

# Simulated attachment metadata and OCR/extracted text for seed tickets.
# In production, this would come from Azure Document Intelligence or similar.

ATTACHMENTS: dict[str, list[dict]] = {}

# --- Valid medical certificate (PDF) for sick leave ticket ---
VALID_DOCTOR_NOTE_PDF = {
    "filename": "arztzeugnis_mueller_2026.pdf",
    "content_type": "application/pdf",
    "size_bytes": 45230,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Praxis Dr. med. Hans Berger\n"
        "Bahnhofstrasse 42, 8001 Zürich\n"
        "Tel: +41 44 123 45 67\n\n"
        "Patient/in: Anna Müller\n"
        "Geburtsdatum: 15.03.1990\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 23.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Hans Berger\n"
        "GLN: 7601000000001"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_mueller_2026.pdf",
}

# --- Invalid attachment: grocery receipt instead of doctor note ---
INVALID_RECEIPT_IMAGE = {
    "filename": "IMG_20260519_receipt.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 128450,
    "extracted_text": (
        "MIGROS\n"
        "Filiale Zürich Hauptbahnhof\n"
        "Datum: 19.05.2026  14:32\n\n"
        "Vollmilch 1L          2.95\n"
        "Brot Ruchbrot          3.40\n"
        "Bananen 1kg            2.80\n"
        "Mineralwasser 6x      6.50\n"
        "Jogurt Nature          1.20\n\n"
        "TOTAL                 16.85\n"
        "Bezahlt: Debitkarte\n"
        "Vielen Dank für Ihren Einkauf!"
    ),
    "url": "https://servicedesk.example.com/attachments/IMG_20260519_receipt.jpg",
}

# --- Valid medical certificate (image/scan) ---
VALID_DOCTOR_NOTE_IMAGE = {
    "filename": "krankmeldung_scan.png",
    "content_type": "image/png",
    "size_bytes": 234500,
    "extracted_text": (
        "ARZTZEUGNIS / CERTIFICAT MÉDICAL\n\n"
        "Dr. med. Claire Fontaine\n"
        "Cabinet médical du Lac\n"
        "Rue du Lac 8, 1003 Lausanne\n"
        "Tél: +41 21 987 65 43\n\n"
        "Patient: Lucas Martin\n"
        "Date de naissance: 22.08.1985\n\n"
        "Date de consultation: 18.05.2026\n\n"
        "Je certifie que le patient susmentionné est en incapacité de travail\n"
        "pour raisons médicales.\n\n"
        "Incapacité: 100%\n"
        "Du: 18.05.2026\n"
        "Au: 25.05.2026\n\n"
        "Signature et cachet\n"
        "Dr. med. Claire Fontaine\n"
        "RCC: Z123456"
    ),
    "url": "https://servicedesk.example.com/attachments/krankmeldung_scan.png",
}

# --- Invalid: certificate with wrong patient name ---
MISMATCHED_NAME_CERTIFICATE = {
    "filename": "arztzeugnis_other_person.pdf",
    "content_type": "application/pdf",
    "size_bytes": 52100,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Peter Roth\n"
        "Marktgasse 12, 3011 Bern\n"
        "Tel: +41 31 456 78 90\n\n"
        "Patient/in: Markus Schneider\n"
        "Geburtsdatum: 05.11.1988\n\n"
        "Datum der Konsultation: 17.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 50%\n"
        "Von: 17.05.2026\n"
        "Bis: 24.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Peter Roth\n"
        "GLN: 7601000000099"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_other_person.pdf",
}

# --- Invalid: expired/old certificate ---
EXPIRED_CERTIFICATE = {
    "filename": "old_certificate_jan2025.pdf",
    "content_type": "application/pdf",
    "size_bytes": 38900,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Maria Keller\n"
        "Steinenvorstadt 5, 4051 Basel\n"
        "Tel: +41 61 234 56 78\n\n"
        "Patient/in: Thomas Weber\n"
        "Geburtsdatum: 30.06.1982\n\n"
        "Datum der Konsultation: 10.01.2025\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 10.01.2025\n"
        "Bis: 17.01.2025\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Maria Keller\n"
        "GLN: 7601000000050"
    ),
    "url": "https://servicedesk.example.com/attachments/old_certificate_jan2025.pdf",
}

# --- INVALID: Completely fictitious doctor (not findable via web search) ---
FICTITIOUS_DOCTOR_CERTIFICATE = {
    "filename": "arztzeugnis_suspicious.pdf",
    "content_type": "application/pdf",
    "size_bytes": 41200,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Xaver Phantomberg\n"
        "Geisterallee 999, 0000 Nirgendwo\n"
        "Tel: +41 00 000 00 00\n\n"
        "Patient/in: Stefan Gruber\n"
        "Geburtsdatum: 14.09.1991\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 30.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Xaver Phantomberg\n"
        "GLN: 0000000000000"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_suspicious.pdf",
}

# --- INVALID: Fake clinic with non-existent address ---
FAKE_CLINIC_CERTIFICATE = {
    "filename": "medical_cert_fakeclinic.pdf",
    "content_type": "application/pdf",
    "size_bytes": 39800,
    "extracted_text": (
        "CERTIFICAT MÉDICAL\n\n"
        "Dr. Jean-Baptiste Inexistant\n"
        "Clinique Fantôme SA\n"
        "Chemin des Nuages 42, 1200 Genève\n"
        "Tél: +41 22 000 00 00\n\n"
        "Patient: Marie Lefevre\n"
        "Date de naissance: 03.07.1995\n\n"
        "Date de consultation: 18.05.2026\n\n"
        "Je certifie que le patient susmentionné est en incapacité de travail\n"
        "pour raisons médicales.\n\n"
        "Incapacité: 100%\n"
        "Du: 18.05.2026\n"
        "Au: 01.06.2026\n\n"
        "Signature et cachet\n"
        "Dr. Jean-Baptiste Inexistant\n"
        "RCC: X000000"
    ),
    "url": "https://servicedesk.example.com/attachments/medical_cert_fakeclinic.pdf",
}

# --- Valid certificate with real-sounding doctor (verifiable) ---
VALID_CERTIFICATE_VERIFIABLE = {
    "filename": "zeugnis_universitaetsspital.pdf",
    "content_type": "application/pdf",
    "size_bytes": 56700,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Universitätsspital Zürich\n"
        "Klinik für Allgemeine Innere Medizin\n"
        "Rämistrasse 100, 8091 Zürich\n"
        "Tel: +41 44 255 11 11\n\n"
        "Behandelnder Arzt: Dr. med. Stefan Mayer\n\n"
        "Patient/in: Katrin Hofmann\n"
        "Geburtsdatum: 22.04.1988\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 100%\n"
        "Von: 19.05.2026\n"
        "Bis: 26.05.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Stefan Mayer\n"
        "Universitätsspital Zürich\n"
        "GLN: 7601000618627"
    ),
    "url": "https://servicedesk.example.com/attachments/zeugnis_universitaetsspital.pdf",
}

# --- Suspicious: valid-looking cert but GLN doesn't match doctor name ---
GLN_MISMATCH_CERTIFICATE = {
    "filename": "arztzeugnis_gln_mismatch.pdf",
    "content_type": "application/pdf",
    "size_bytes": 44100,
    "extracted_text": (
        "ÄRZTLICHES ZEUGNIS\n\n"
        "Dr. med. Andreas Widmer\n"
        "Praxis am See\n"
        "Seestrasse 15, 6004 Luzern\n"
        "Tel: +41 41 345 67 89\n\n"
        "Patient/in: Rolf Meier\n"
        "Geburtsdatum: 11.12.1979\n\n"
        "Datum der Konsultation: 19.05.2026\n\n"
        "Hiermit bestätige ich, dass oben genannte Person aus gesundheitlichen "
        "Gründen arbeitsunfähig ist.\n\n"
        "Arbeitsunfähigkeit: 50%\n"
        "Von: 19.05.2026\n"
        "Bis: 02.06.2026\n\n"
        "Stempel und Unterschrift\n"
        "Dr. med. Andreas Widmer\n"
        "GLN: 7601000000001"
    ),
    "url": "https://servicedesk.example.com/attachments/arztzeugnis_gln_mismatch.pdf",
}

# =====================================================
# EXPENSE REIMBURSEMENT ATTACHMENTS
# =====================================================

# --- Valid hotel invoice for business trip ---
VALID_HOTEL_INVOICE = {
    "filename": "hotel_rechnung_muenchen_2026.pdf",
    "content_type": "application/pdf",
    "size_bytes": 67800,
    "extracted_text": (
        "RECHNUNG / INVOICE\n\n"
        "Hotel Königshof München\n"
        "Karlsplatz 25, 80335 München, Deutschland\n"
        "Tel: +49 89 551 360\n"
        "Steuer-Nr: DE 123456789\n\n"
        "Rechnungsnummer: INV-2026-05-8847\n"
        "Datum: 16.05.2026\n\n"
        "Gast: Sandra Huber\n"
        "Check-in: 14.05.2026\n"
        "Check-out: 16.05.2026\n\n"
        "POSITIONEN:\n"
        "14.05.2026  Einzelzimmer Business      EUR 165.00\n"
        "15.05.2026  Einzelzimmer Business      EUR 165.00\n"
        "14.05.2026  Frühstück Buffet            EUR  22.00\n"
        "15.05.2026  Frühstück Buffet            EUR  22.00\n"
        "            City Tax (2 Nächte)          EUR   7.50\n"
        "-------------------------------------------\n"
        "NETTO                                   EUR 381.50\n"
        "MwSt. 7%                                EUR  26.71\n"
        "-------------------------------------------\n"
        "GESAMTBETRAG                            EUR 408.21\n\n"
        "Bezahlt per: Firmenkreditkarte\n"
        "Kartennr: **** **** **** 4521\n\n"
        "Vielen Dank für Ihren Aufenthalt!\n"
        "Wir freuen uns auf Ihren nächsten Besuch."
    ),
    "url": "https://servicedesk.example.com/attachments/hotel_rechnung_muenchen_2026.pdf",
}

# --- Valid train ticket for business trip ---
VALID_TRAIN_TICKET = {
    "filename": "sbb_ticket_zuerich_muenchen.pdf",
    "content_type": "application/pdf",
    "size_bytes": 23400,
    "extracted_text": (
        "SBB CFF FFS\n"
        "FAHRAUSWEIS / BILLET\n\n"
        "Buchungsnummer: X7K9M2\n"
        "Kaufdatum: 10.05.2026\n\n"
        "Reisender: Sandra Huber\n\n"
        "HINFAHRT:\n"
        "14.05.2026  Zürich HB → München Hbf\n"
        "Abfahrt: 06:32  Ankunft: 10:14\n"
        "ICE 72, 2. Klasse, Sitzplatz 45\n\n"
        "RÜCKFAHRT:\n"
        "16.05.2026  München Hbf → Zürich HB\n"
        "Abfahrt: 17:21  Ankunft: 21:03\n"
        "ICE 79, 2. Klasse, Sitzplatz 62\n\n"
        "Preis: CHF 95.00 (Spartageskarte)\n\n"
        "Bezahlt: Kreditkarte\n"
        "Dieser Fahrausweis ist nicht übertragbar."
    ),
    "url": "https://servicedesk.example.com/attachments/sbb_ticket_zuerich_muenchen.pdf",
}

# --- Valid taxi receipt ---
VALID_TAXI_RECEIPT = {
    "filename": "taxi_quittung_muenchen.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 89200,
    "extracted_text": (
        "TAXIQUITTUNG\n\n"
        "Münchner Taxi-Zentrale\n"
        "Fahrzeug-Nr: M-TX 4892\n\n"
        "Datum: 14.05.2026\n"
        "Uhrzeit: 10:25 - 10:48\n\n"
        "Von: München Hbf\n"
        "Nach: Messegelände München\n\n"
        "Fahrpreis:          EUR 32.40\n"
        "inkl. MwSt. 7%\n\n"
        "Bezahlt: Bar\n"
        "Quittungsnr: TQ-2026-14052"
    ),
    "url": "https://servicedesk.example.com/attachments/taxi_quittung_muenchen.jpg",
}

# --- Suspicious expense: personal dinner receipt ---
PERSONAL_DINNER_RECEIPT = {
    "filename": "restaurant_rechnung.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 112300,
    "extracted_text": (
        "RESTAURANT GOLDENER HIRSCH\n"
        "Altstadt 17, 80331 München\n\n"
        "Datum: 15.05.2026\n"
        "Tisch 8 / Kellner: Mario\n\n"
        "2x Wiener Schnitzel         EUR 38.00\n"
        "1x Kalbsfilet                EUR 42.00\n"
        "1x Flasche Rotwein Barolo   EUR 89.00\n"
        "2x Tiramisu                  EUR 18.00\n"
        "1x Grappa                    EUR 12.00\n"
        "---\n"
        "Zwischensumme               EUR 199.00\n"
        "Trinkgeld                    EUR  30.00\n"
        "---\n"
        "TOTAL                        EUR 229.00\n\n"
        "Bewirtet: 2 Personen\n"
        "Bezahlt: Kreditkarte\n"
        "Vielen Dank und Auf Wiedersehen!"
    ),
    "url": "https://servicedesk.example.com/attachments/restaurant_rechnung.jpg",
}

# --- Invalid: expense claim with inflated/altered receipt ---
ALTERED_RECEIPT = {
    "filename": "hotel_invoice_altered.pdf",
    "content_type": "application/pdf",
    "size_bytes": 71200,
    "extracted_text": (
        "RECHNUNG\n\n"
        "Hotel Garni Zentrum\n"
        "Schillerstrasse 8, 80336 München\n\n"
        "Rechnungsnummer: R-9921\n"
        "Datum: 16.05.2026\n\n"
        "Gast: Marco Bernasconi\n"
        "Check-in: 14.05.2026\n"
        "Check-out: 16.05.2026\n\n"
        "2 Nächte Deluxe Suite        EUR 450.00\n"
        "Minibar                       EUR 120.00\n"
        "Spa & Wellness                EUR  85.00\n"
        "Zimmerservice                  EUR  65.00\n"
        "---\n"
        "TOTAL                          EUR 720.00\n\n"
        "Bezahlt: Überweisung\n\n"
        "[Note: Font size inconsistencies detected in OCR. "
        "Amount fields appear to use different typeface than rest of document.]"
    ),
    "url": "https://servicedesk.example.com/attachments/hotel_invoice_altered.pdf",
}
