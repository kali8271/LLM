from fpdf import FPDF
import os

output_dir = "app/data/documents"
os.makedirs(output_dir, exist_ok=True)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Sample Contract Document", ln=True, align="C")
pdf.ln(10)
pdf.multi_cell(0, 10, txt="""
SECTION 1: PARTIES
This Agreement is made between Alpha Corp and Beta LLC.

SECTION 2: TERMS
Alpha Corp agrees to deliver 100 widgets to Beta LLC for a total amount of $10,000.

SECTION 3: JURISDICTION
Jurisdiction: California.

SECTION 4: SIGNATURES
Signed by both parties on January 1, 2024.
""")

pdf.output(os.path.join(output_dir, "sample_contract.pdf"))
print("Sample PDF generated at app/data/documents/sample_contract.pdf")