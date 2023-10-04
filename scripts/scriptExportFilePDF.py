from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Nombre del archivo PDF que deseas crear
nombre_archivo = 'C:/Users/a1749/Desktop/Documentacion/mi_archivo.pdf'

# Crear un archivo PDF
c = canvas.Canvas(nombre_archivo, pagesize=letter)

# Agregar texto al PDF
texto = "Este es un ejemplo de texto en un archivo PDF creado con Python y ReportLab."
c.drawString(100, 600, texto)

# Guardar el PDF
c.showPage()
c.save()

print(f"El archivo PDF '{nombre_archivo}' se ha creado con éxito.")
