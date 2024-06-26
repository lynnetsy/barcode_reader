import fitz  # PyMuPDF
from PIL import Image
from pyzbar.pyzbar import decode
import io
import cv2
import numpy as np


def extract_images_from_pdf(pdf_path):
    """Extrae todas las imágenes de un archivo PDF."""
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
            # Guardar la imagen para verificación
            image.save(f"extracted_image_{page_num}_{img_index}.png")
            print(f"Imagen extraída: extracted_image_{page_num}_{img_index}.png")
    return images


def read_barcode_from_image(image):
    """Lee el código de barras de una imagen de PIL."""
    # Convertir la imagen a escala de grises y mejorar el contraste
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    image_cv = cv2.adaptiveThreshold(image_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    barcodes = decode(image_cv)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        print(f"Encontrado código de barras: {barcode_data}, Tipo: {barcode_type}")
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
    print(f"PDF rotado guardado como: {rotated_pdf_path}")
    return rotated_pdf_path


def process_images_for_barcodes(images):
    """Procesa una lista de imágenes y lee los códigos de barras."""
    barcodes = []
    for image in images:
        barcode, barcode_type = read_barcode_from_image(image)
        if barcode is not None:
            barcodes.append({
                "content": barcode,
                "type": barcode_type
            })
    return barcodes


def process_pdf_with_rotation(pdf_path, angle=0):
    """Procesa un PDF con un ángulo de rotación específico y lee los códigos de barras."""
    if angle != 0:
        rotated_pdf_path = rotate_pdf(pdf_path, angle)
        print("Rotated PDF Path: ", rotated_pdf_path)
        images = extract_images_from_pdf(rotated_pdf_path)
        print("Images 90 rotation: ", images)
    else:   
        images = extract_images_from_pdf(pdf_path)
        print("Images 0 rotation: ", images)
    return process_images_for_barcodes(images)


def process_pdf_for_barcodes(pdf_path, angle=0):
    """Procesa un archivo PDF y lee los códigos de barras de las imágenes extraídas."""
    barcodes = process_pdf_with_rotation(pdf_path, angle)
    return barcodes


# Ejemplo de uso
if __name__ == "__main__":
    
    pdf_path = '../examples/comp_dom_rotado_rotated_90.pdf'
    barcodes = process_pdf_for_barcodes(pdf_path, 0)
    print("::: barcodes result", barcodes)
    if len(barcodes) == 0:
        print('No se encontró ningún código de barras en el PDF.')
        # barcodes_with_rotation = process_pdf_with_rotation(pdf_path, 90)
    else:
        for barcode in barcodes:
            print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
