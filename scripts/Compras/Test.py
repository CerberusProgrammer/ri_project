from xhtml2pdf import pisa
from io import BytesIO

def convert_html_to_pdf(input_html, output_pdf):
    # Lee el contenido del archivo HTML de entrada
    with open(input_html, 'rb') as html_file:
        html_content = html_file.read()

    # Crea un objeto BytesIO para almacenar el PDF generado
    pdf_buffer = BytesIO()

    # Convierte el HTML en un archivo PDF
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err: # type: ignore
        print("Error al generar el PDF")
    else:
        # Guarda el PDF en un archivo
        with open(output_pdf, 'wb') as pdf_file:
            pdf_file.write(pdf_buffer.getvalue())
        print("PDF generado exitosamente")

if __name__ == "__main__":
    input_html = 'C:/Users/a1749/ri_project/scripts/Compras/Testxhtml2pdf.html'  # Ruta del archivo HTML de entrada
    output_pdf = 'C:/Users/a1749/ri_project/scripts/Compras/Testxhtml2pdf.pdf'  # Ruta del archivo PDF de salida

    convert_html_to_pdf(input_html, output_pdf)
