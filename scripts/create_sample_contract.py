import fitz

document = fitz.open()
page = document.new_page()

contract_text = """
SERVICE AGREEMENT

1. Definitions

This agreement is between ABC Technologies and XYZ Solutions.

2. Payment Terms

The customer shall pay INR 50,000 every month.

3. Confidentiality

Both parties shall maintain confidentiality
of all shared information.

4. Termination

Either party may terminate this agreement
with 30 days written notice.
"""

page.insert_textbox(
    fitz.Rect(50, 50, 550, 750),
    contract_text,
    fontsize=12
)

document.save("dataset/sample_contract.pdf")
document.close()

print("Sample contract PDF created successfully.")
