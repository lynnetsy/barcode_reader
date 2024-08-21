import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
from pyzbar.pyzbar import decode
import io
import cv2
import os

def rotate_pdf(input_pdf_path, angle, output_pdf_path):
    """Rota todas las páginas de un archivo PDF por el ángulo especificado y guarda un nuevo archivo PDF."""
    with open(input_pdf_path, "rb") as input_pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfFileWriter()

        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            page.rotateClockwise(angle)
            pdf_writer.addPage(page)

        with open(output_pdf_path, "wb") as output_pdf_file:
            pdf_writer.write(output_pdf_file)
    
    print(f"PDF rotado guardado como: {output_pdf_path}")
    return output_pdf_path

def extract_images_from_pdf(pdf_path, n_extraccion=0):
    """Extrae todas las imágenes de un archivo PDF usando pdf2image."""
    pdf_directory = os.path.dirname(pdf_path)
    
    # Crear la carpeta 'extracted_images' si no existe
    extracted_images_dir = os.path.join(pdf_directory, 'extracted_images')
    if not os.path.exists(extracted_images_dir):
        os.makedirs(extracted_images_dir)
    images = convert_from_path(pdf_path)
    # Convertir PDF a imágenes
    images = convert_from_path(pdf_path)
    extracted_images = []
    for page_num, image in enumerate(images):
        # Guardar la imagen en la carpeta 'extracted_images'
        image_path = os.path.join(extracted_images_dir, f"{n_extraccion}_extracted_page_{page_num}.png")
        image.save(image_path, 'PNG')
        extracted_images.append(image)
        print(f"Imagen extraída: {image_path}")
    
    return extracted_images

def read_barcode_from_image(image):
    """Lee el código de barras de una imagen de PIL."""
    barcodes = decode(image)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        print(f"Encontrado código de barras: {barcode_data}, Tipo: {barcode_type}")
        return barcode_data, barcode_type
    return None, None

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

def process_image_file(image_path):
    """Procesa un archivo de imagen (.jpg, .png) para leer códigos de barras."""
    try:
        image = Image.open(image_path)
        return process_images_for_barcodes([image])
    except Exception as e:
        print(f"Error procesando la imagen {image_path}: {e}")
        return []

def process_pdf_for_barcodes(pdf_path, angle=0, n_extraccion=0):
    """Procesa un PDF con un ángulo de rotación específico y lee los códigos de barras."""
    if angle != 0:
        rotated_pdf_path = pdf_path.replace(".pdf", f"_rotated_{angle}.pdf")
        rotated_pdf_path = rotate_pdf(pdf_path, angle, rotated_pdf_path)
        images = extract_images_from_pdf(rotated_pdf_path, n_extraccion)
    else:
        images = extract_images_from_pdf(pdf_path, n_extraccion)

    return process_images_for_barcodes(images)

def process_files(input_path):
    """Procesa archivos PDF e imágenes individualmente o en un directorio."""
    total_files = 0
    failed_files = 0
    
    # Procesar un solo archivo
    if os.path.isfile(input_path):
        if input_path.endswith(".pdf"):
            total_files += 1
            print(f"Procesando archivo PDF: {input_path}")
            n_extraccion = 0
            barcodes = process_pdf_for_barcodes(input_path, 0, n_extraccion)
            print("Resultados de códigos de barras:", barcodes)
            
            if len(barcodes) == 0:
                n_extraccion += 1
                print('No se encontró ningún código de barras en el PDF. Intentando con rotación de 90 grados.')
                barcodes_with_rotation = process_pdf_for_barcodes(input_path, 90, n_extraccion)
                if len(barcodes_with_rotation) == 0:
                    failed_files += 1
                    print('No se encontró ningún código de barras en el PDF incluso después de la rotación.')
                else:
                    for barcode in barcodes_with_rotation:
                        print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
            else:
                for barcode in barcodes:
                    print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
        elif input_path.lower().endswith((".jpg", ".jpeg", ".png")):
            total_files += 1
            print(f"Procesando archivo de imagen: {input_path}")
            barcodes = process_image_file(input_path)
            if len(barcodes) == 0:
                failed_files += 1
                print(f"No se encontró ningún código de barras en la imagen {input_path}.")
            else:
                for barcode in barcodes:
                    print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
        else:
            print(f"{input_path} no es un archivo PDF o de imagen válido.")
    
    # Procesar un directorio
    elif os.path.isdir(input_path):
        print(f"Procesando todos los archivos en la carpeta: {input_path}")
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if filename.endswith(".pdf"):
                total_files += 1
                print(f"Procesando archivo PDF: {file_path}")
                n_extraccion = 0
                barcodes = process_pdf_for_barcodes(file_path, 0, n_extraccion)
                print("Resultados de códigos de barras:", barcodes)
                
                if len(barcodes) == 0:
                    n_extraccion += 1
                    print('No se encontró ningún código de barras en el PDF. Intentando con rotación de 90 grados.')
                    barcodes_with_rotation = process_pdf_for_barcodes(file_path, 90, n_extraccion)
                    if len(barcodes_with_rotation) == 0:
                        failed_files += 1
                        print('No se encontró ningún código de barras en el PDF incluso después de la rotación.')
                    else:
                        for barcode in barcodes_with_rotation:
                            print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
                else:
                    for barcode in barcodes:
                        print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
            elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
                total_files += 1
                print(f"Procesando archivo de imagen: {file_path}")
                barcodes = process_image_file(file_path)
                if len(barcodes) == 0:
                    failed_files += 1
                    print(f"No se encontró ningún código de barras en la imagen {file_path}.")
                else:
                    for barcode in barcodes:
                        print(f'Tipo: {barcode["type"]}, Contenido: {barcode["content"]}')
    else:
        print(f"{input_path} no es un archivo ni una carpeta válida.")
    
    # Imprimir resultados finales
    print(f"Total de archivos procesados: {total_files}")
    print(f"Total de archivos sin código de barras: {failed_files}")