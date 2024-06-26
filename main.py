from src.barcodereader import process_pdf_for_barcodes

def read_pdf():
    # examples/
    pdf_path = "/app/examples/comp_dom_rotated_90.pdf"
    pdf_data = process_pdf_for_barcodes(pdf_path)
    print("::: barcodes result", pdf_data)

if __name__ == "__main__":
    read_pdf()
