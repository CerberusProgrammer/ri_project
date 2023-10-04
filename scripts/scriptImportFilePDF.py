import PyPDF2

try:
    with open('C:/Users/a1749/Desktop/Documentacion/FORM-PC001 Orden de Compra.pdf', 'rb') as pdf_file:
        # Utiliza PdfReader en lugar de PdfFileReader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Comprueba el número total de páginas en el PDF
        num_pages = len(pdf_reader.pages)

        # Crea una cadena vacía para almacenar el texto extraído
        text = ""

        # Itera a través de todas las páginas del PDF
        for page_num in range(num_pages):
            # Extrae el texto de la página actual
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()

            # Concatena el texto extraído a la cadena principal
            text += page_text

        # Imprime el texto extraído del PDF
        print(text)
except FileNotFoundError:
    print("El archivo PDF no se encontró en la ubicación especificada.")
except Exception as e:
    print(f"Se produjo un error: {str(e)}")




