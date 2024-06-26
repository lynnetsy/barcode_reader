import fitz  # PyMuPDF
from PIL import Image
from pyzbar.pyzbar import decode
import io

def extract_images_from_pdf(pdf_path):
    """Extrae todas las imágenes de un archivo PDF."""
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        for _, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
    return images

def read_barcode_from_image(image):
    """Lee el código de barras de una imagen de PIL."""
    barcodes = decode(image)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        return barcode_data, barcode_type
    return None, None

def rotate_pdf(pdf_path, angle):
    """Rota todas las páginas de un archivo PDF por el ángulo especificado y guarda un nuevo archivo PDF."""
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        page.set_rotation(angle)
    rotated_pdf_path = pdf_path.replace(".pdf", f"_rotated_{angle}.pdf")
    pdf_document.save(rotated_pdf_path)
    return rotated_pdf_path

def process_pdf_for_barcodes(pdf_path):
    """Procesa un archivo PDF y lee los códigos de barras de las imágenes extraídas."""
    images = extract_images_from_pdf(pdf_path)
    barcodes = list()
    for image in images:
        barcode, type = read_barcode_from_image(image)
        if barcode is not None:
            barcodes.append({
                "content": barcode,
                "type": type
            })
        else:
            barcodes.append(None)
    # if barcodes is None rota todas las paginas del pdf
    if not any(barcodes):
        rotated_pdf = rotate_pdf(pdf_path, 90)
        images = extract_images_from_pdf(rotated_pdf)
    return barcodes
