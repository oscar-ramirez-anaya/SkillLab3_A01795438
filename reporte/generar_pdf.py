import io
import os
import re
import subprocess

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "SkillLab3_A01795438.pdf")
PIE = "Skill Lab 3 · A01795438 · IA5004.10"
# títulos en el mismo orden que los marcadores {P1}..{Pn} del índice
TITULOS = [
    "1. Contexto y método", "1.1 El caso y su relación con el Aprende", "1.2 Datos comunes y modalidad",
    "2. Parte A: la mesa de contexto", "2.1 Los tres paquetes", "2.2 Elección del paquete y límites de la comparación",
    "3. Parte B: la aduana de acciones", "3.1 Reglas de la aduana", "3.2 Registro de ejecución",
    "3.3 Propuesta del enrutador frente a autorización", "4. Ruptura y reversibilidad", "4.1 La aduana apagada",
    "4.2 Clase y costo de corregir cada entrada indebida", "5. Los cinco resultados del resumen", "6. Conclusiones",
    "Apéndice A. Declaración de uso de IA", "Glosario", "Referencias",
]


def plano(texto):
    return re.sub(r"\s+", "", texto)


def render(html, pdf):
    ruta = os.path.join(AQUI, "_tmp.html")
    open(ruta, "w", encoding="utf-8").write(html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", f"file://{ruta}"], check=True, capture_output=True)
    os.remove(ruta)


def paginas(pdf):
    textos = [plano(p.extract_text()) for p in PdfReader(pdf).pages]
    # portada (1) e índice (2) se ignoran: en el índice aparecen todos los títulos
    return [next(i + 1 for i, x in enumerate(textos) if i >= 2 and plano(t) in x) for t in TITULOS]


plantilla = open(os.path.join(AQUI, "reporte_tpl.html"), encoding="utf-8").read()
tmp = os.path.join(AQUI, "_tmp.pdf")
html = plantilla
for _ in range(2):
    render(html, tmp)
    nums = paginas(tmp)
    html = plantilla
    for i, n in sorted(enumerate(nums, 1), reverse=True):
        html = html.replace("{P%d}" % i, str(n))
render(html, tmp)
print("páginas por sección:", paginas(tmp))

lector = PdfReader(tmp)
total = len(lector.pages)
escritor = PdfWriter()
for i, pagina in enumerate(lector.pages, 1):
    if i > 1:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.setStrokeColorRGB(0.78, 0.8, 0.84)
        c.setLineWidth(0.6)
        c.line(54, 40, letter[0] - 54, 40)
        c.setFont("Times-Roman", 8.5)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(54, 28, PIE)
        c.drawRightString(letter[0] - 54, 28, f"Página {i} de {total}")
        c.save()
        buf.seek(0)
        pagina.merge_page(PdfReader(buf).pages[0])
    escritor.add_page(pagina)
escritor.add_metadata({"/Title": "SkillLab3_A01795438", "/Author": "Oscar Alberto Ramírez Anaya",
                       "/Producer": "", "/Creator": ""})
with open(SALIDA, "wb") as f:
    escritor.write(f)
os.remove(tmp)
print("total", total)
