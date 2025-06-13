from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def create_watermark(output_path= os.path.join('media', 'watermark.pdf')  , text='© www.MzansiPlug.com'):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setFont("Helvetica", 40)
    c.setFillColorRGB(0.6, 0.6, 0.6, alpha=0.3)  
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()

create_watermark()
