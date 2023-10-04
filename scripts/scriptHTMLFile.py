from xhtml2pdf import pisa

# Ruta al archivo HTML que deseas convertir
archivo_html = 'C:/Users/a1749/ri_project/scripts/archivo.html'

# Ruta donde se guardará el archivo PDF resultante
archivo_pdf = 'C:/Users/a1749/ri_project/scripts/archivo.pdf'

# Abrir el archivo HTML en modo lectura
with open(archivo_html, 'rb') as fuente_html:
    # Crear un archivo PDF vacío donde se escribirá la salida
    with open(archivo_pdf, 'wb') as archivo_salida_pdf:
        # Utilizar pisa para convertir el HTML a PDF
        pisa_status = pisa.CreatePDF(fuente_html, archivo_salida_pdf)
        
# Comprobar el estado de la conversión
if pisa_status.err: # type: ignore
    print("Se produjo un error durante la conversión.")
else:
    print(f'Se ha creado el archivo PDF en: {archivo_pdf}')
