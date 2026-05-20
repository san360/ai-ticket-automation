"""Generate realistic PDF and image files from attachment_data.py text content.

This script renders the extracted_text from each attachment into actual PDF/image
files, then base64-encodes them and updates attachment_data.py with file_data fields.

Run this whenever attachment content changes:
    python scripts/generate_attachments.py

Requires: fpdf2, Pillow
    pip install fpdf2 Pillow
"""

import base64
import io
import os
import sys
import textwrap

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "servicedesk-simulator", "attachments")


def generate_pdf(text: str, filename: str, title: str = "") -> bytes:
    """Render text content into a realistic-looking PDF with proper formatting."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Use built-in font - replace unsupported Unicode chars with ASCII equivalents
    text = text.replace("\u2192", "->").replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    pdf.set_font("Helvetica", size=10)

    # Title/header area
    if title:
        pdf.set_font("Helvetica", "B", size=14)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(5)

    # Render each line with proper formatting
    pdf.set_font("Helvetica", size=10)
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()

        # Detect headers (ALL CAPS lines)
        if stripped and stripped == stripped.upper() and len(stripped) > 3 and not stripped.startswith("---"):
            pdf.set_font("Helvetica", "B", size=12)
            pdf.ln(3)
            pdf.cell(0, 6, stripped, ln=True)
            pdf.set_font("Helvetica", size=10)
        # Detect separator lines
        elif stripped.startswith("---"):
            pdf.ln(2)
            pdf.cell(0, 4, "_" * 60, ln=True)
            pdf.ln(2)
        # Detect line items with amounts (contains EUR/CHF and numbers)
        elif ("EUR" in stripped or "CHF" in stripped) and any(c.isdigit() for c in stripped):
            pdf.set_font("Courier", size=10)
            # Truncate long lines to fit page width
            safe_line = stripped[:85] if len(stripped) > 85 else stripped
            pdf.cell(0, 5, safe_line, ln=True)
            pdf.set_font("Helvetica", size=10)
        # Empty lines
        elif not stripped:
            pdf.ln(4)
        # Regular text
        else:
            # Wrap long lines
            wrapped = textwrap.wrap(stripped, width=80)
            for wline in wrapped:
                pdf.cell(0, 5, wline, ln=True)

    return pdf.output()


def generate_receipt_image(text: str, filename: str) -> bytes:
    """Render receipt/ticket text as a realistic receipt-style image."""
    # Receipt-style: narrow, tall, monospace font on white/off-white background
    lines = text.split("\n")
    line_height = 22
    margin = 30
    width = 500
    height = margin * 2 + len(lines) * line_height + 40

    # Create image with slight off-white background (like thermal paper)
    img = Image.new("RGB", (width, height), color=(252, 250, 245))
    draw = ImageDraw.Draw(img)

    # Try to use a monospace font, fall back to default
    try:
        font = ImageFont.truetype("consola.ttf", 14)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("cour.ttf", 14)
        except (OSError, IOError):
            font = ImageFont.load_default()

    y = margin
    for line in lines:
        # Bold-style for headers (draw twice with 1px offset)
        if line.strip() and line.strip() == line.strip().upper() and len(line.strip()) > 3:
            draw.text((margin, y), line, fill=(0, 0, 0), font=font)
            draw.text((margin + 1, y), line, fill=(0, 0, 0), font=font)
        elif "---" in line:
            draw.line([(margin, y + 10), (width - margin, y + 10)], fill=(100, 100, 100), width=1)
        else:
            draw.text((margin, y), line, fill=(30, 30, 30), font=font)
        y += line_height

    # Convert to JPEG bytes
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()


def generate_scan_image(text: str, filename: str) -> bytes:
    """Render a document scan as a PNG image (like a scanned medical certificate)."""
    lines = text.split("\n")
    line_height = 24
    margin = 50
    width = 700
    height = margin * 2 + len(lines) * line_height + 60

    # Slightly gray background to simulate scanned paper
    img = Image.new("RGB", (width, height), color=(245, 245, 240))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except (OSError, IOError):
        font = ImageFont.load_default()
        font_bold = font

    y = margin
    for line in lines:
        stripped = line.strip()
        if stripped and stripped == stripped.upper() and len(stripped) > 3:
            draw.text((margin, y), stripped, fill=(0, 0, 0), font=font_bold)
        elif not stripped:
            pass  # empty line, just add spacing
        else:
            draw.text((margin, y), line, fill=(20, 20, 20), font=font)
        y += line_height

    # Add a faint "stamp" circle in bottom-right to simulate doctor's stamp
    stamp_x, stamp_y = width - 150, height - 130
    draw.ellipse([stamp_x, stamp_y, stamp_x + 80, stamp_y + 80], outline=(0, 0, 150, 80), width=2)
    draw.text((stamp_x + 15, stamp_y + 30), "STAMP", fill=(0, 0, 150), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def main():
    """Generate all attachment files and write base64 data."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Import attachment data
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "servicedesk-simulator"))
    from attachment_data import (
        VALID_DOCTOR_NOTE_PDF,
        INVALID_RECEIPT_IMAGE,
        VALID_DOCTOR_NOTE_IMAGE,
        MISMATCHED_NAME_CERTIFICATE,
        EXPIRED_CERTIFICATE,
        FICTITIOUS_DOCTOR_CERTIFICATE,
        FAKE_CLINIC_CERTIFICATE,
        VALID_CERTIFICATE_VERIFIABLE,
        GLN_MISMATCH_CERTIFICATE,
        VALID_HOTEL_INVOICE,
        VALID_TRAIN_TICKET,
        VALID_TAXI_RECEIPT,
        PERSONAL_DINNER_RECEIPT,
        ALTERED_RECEIPT,
    )

    attachments = [
        # PDFs (medical certificates and invoices)
        (VALID_DOCTOR_NOTE_PDF, "pdf"),
        (MISMATCHED_NAME_CERTIFICATE, "pdf"),
        (EXPIRED_CERTIFICATE, "pdf"),
        (FICTITIOUS_DOCTOR_CERTIFICATE, "pdf"),
        (FAKE_CLINIC_CERTIFICATE, "pdf"),
        (VALID_CERTIFICATE_VERIFIABLE, "pdf"),
        (GLN_MISMATCH_CERTIFICATE, "pdf"),
        (VALID_HOTEL_INVOICE, "pdf"),
        (VALID_TRAIN_TICKET, "pdf"),
        (ALTERED_RECEIPT, "pdf"),
        # Images (scans and receipts)
        (VALID_DOCTOR_NOTE_IMAGE, "scan"),
        (INVALID_RECEIPT_IMAGE, "receipt"),
        (VALID_TAXI_RECEIPT, "receipt"),
        (PERSONAL_DINNER_RECEIPT, "receipt"),
    ]

    results = {}
    for attachment, render_type in attachments:
        filename = attachment["filename"]
        text = attachment["extracted_text"]
        content_type = attachment["content_type"]

        print(f"Generating: {filename} ({render_type})...", end=" ")

        try:
            if render_type == "pdf":
                data = generate_pdf(text, filename)
            elif render_type == "receipt":
                data = generate_receipt_image(text, filename)
            elif render_type == "scan":
                data = generate_scan_image(text, filename)
            else:
                continue
        except Exception as e:
            print(f"FAILED: {e}")
            continue

        # Save file
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "wb") as f:
            f.write(data)

        # Base64 encode
        b64 = base64.b64encode(data).decode("utf-8")
        results[filename] = {
            "file_data": f"data:{content_type};base64,{b64}",
            "size_bytes": len(data),
        }
        print(f"-> {len(data)} bytes")

    # Write a JSON manifest for the simulator to load at startup
    import json
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    # Only store file paths (not inline base64 in manifest - too large)
    manifest = {fname: {"size_bytes": info["size_bytes"]} for fname, info in results.items()}
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nGenerated {len(results)} attachment files in: {OUTPUT_DIR}")
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
