from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf.util import ErrorMsg

# Variables que deseas inyectar en el HTML
variables = {
    'Nombre': 'John Doe',
    'RFC': 'ABCD123456',
    'Domicilio': '123 Main St',
    'Telefono': '555-123-456',
    'Correo': 'john.doe@example.com',
    'Localidad': 'Mexicali',
    'Colonia': 'Roble',
    'Estado': 'Baja California',
    'Codigo': '12345',
    'Pais': 'Mexico',
}

# Directorio donde se encuentra el archivo HTML
template_dir = 'C:/Users/a1749/ri_project/scripts/OrdenDeCompra/'

# Nombre del archivo HTML
template_file = 'OrdenDeCompra.html'

# Carga el entorno de Jinja2
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template(template_file)

# Renderiza el HTML con las variables
html_content = template.render(variables=variables)

# Crea un objeto BytesIO para almacenar el PDF generado
pdf_buffer = BytesIO()

# Convierte el HTML en un archivo PDF
pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

if pisa_status.err:  # type: ignore
    print("Error al generar el PDF")
else:
    # Guarda el PDF en un archivo
    with open('C:/Users/a1749/ri_project/scripts/OrdenDeCompra.pdf', 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())
    print("PDF generado exitosamente")

