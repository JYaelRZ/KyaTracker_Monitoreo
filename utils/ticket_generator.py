import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime

def generate_monitoring_ticket_pdf(output_path, folio, client_name, unit, origin, destination, start_time, arrival_time, billed_minutes, total_amount):
    """
    Genera un comprobante de servicio de monitoreo logístico.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=30)
    Story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2D6ADF'),
        spaceAfter=5,
        alignment=0 # Left
    )
    
    sub_title_style = ParagraphStyle(
        'CustomSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=0 # Left
    )

    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_ticket.png")
    if os.path.exists(logo_path):
        try:
            from reportlab.lib.utils import ImageReader
            img_reader = ImageReader(logo_path)
            mw, mh = img_reader.getSize()
            aspect = mh / float(mw)
            target_width = 200
            target_height = target_width * aspect
            img = RLImage(logo_path, width=target_width, height=target_height)
            img.hAlign = 'CENTER'
            Story.append(img)
            Story.append(Spacer(1, 15))
        except Exception:
            pass

    Story.append(Paragraph("TICKET DE MONITOREO Y CUSTODIA", title_style))
    Story.append(Paragraph("KYATRACKER - SERVICIOS SATELITALES Y SEGURIDAD", sub_title_style))
    Story.append(Spacer(1, 10))
    
    date_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    
    data_info = [
        ["Folio de Servicio:", f"#{folio}"],
        ["Fecha de Emisión:", date_str],
        ["Cliente:", client_name],
        ["Unidad:", unit]
    ]
    t_info = Table(data_info, colWidths=[200, 300], hAlign='LEFT')
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#333333'))
    ]))
    Story.append(t_info)
    Story.append(Spacer(1, 20))
    
    Story.append(Paragraph("Detalles de la Ruta y Tiempos", styles['Heading3']))
    Story.append(Spacer(1, 5))
    
    data_trans = [
        ["Origen:", origin],
        ["Destino:", destination],
        ["Hora de Salida:", start_time],
        ["Hora de Llegada:", arrival_time if arrival_time else "En Ruta"],
        ["Minutos Cobrados:", f"{billed_minutes} mins" if billed_minutes else "Pendiente"],
        ["Total del Servicio:", f"${total_amount:.2f} MXN" if total_amount else "Pendiente"],
    ]
    
    t_trans = Table(data_trans, colWidths=[200, 300], hAlign='LEFT')
    t_trans.setStyle(TableStyle([
        ('BACKGROUND', (0,-1), (1,-1), colors.HexColor('#DBEAFE')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    Story.append(t_trans)
    Story.append(Spacer(1, 40))
    
    disclaimer = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        alignment=1 # Center
    )
    Story.append(Paragraph("Este comprobante financiero es generado automáticamente por el Sistema Gestor KyaTracker y ampara el servicio de monitoreo y custodia logística brindado en las fechas y horarios marcados.", disclaimer))
    
    Story.append(Spacer(1, 20))
    
    thanks_style = ParagraphStyle(
        'Thanks',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2D6ADF'),
        alignment=1 # Center
    )
    Story.append(Paragraph("¡Gracias por su preferencia y confianza!", thanks_style))
    
    def draw_bg_logos(canvas, doc):
        import os
        base_dir = os.path.dirname(os.path.dirname(__file__))
        logo_sup = os.path.join(base_dir, "static", "img", "Logosuperior.png")
        logo_inf = os.path.join(base_dir, "static", "img", "logoinferior.png")
        
        if os.path.exists(logo_sup):
            # Top right
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_sup)
            mw, mh = img.getSize()
            aspect = mh / float(mw)
            w = 90
            h = w * aspect
            canvas.drawImage(logo_sup, doc.pagesize[0] - w - 20, doc.pagesize[1] - h - 20, width=w, height=h, mask='auto')
            
        if os.path.exists(logo_inf):
            # Bottom left
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_inf)
            mw, mh = img.getSize()
            aspect = mh / float(mw)
            w = 120
            h = w * aspect
            canvas.drawImage(logo_inf, 20, 20, width=w, height=h, mask='auto')

    doc.build(Story, onFirstPage=draw_bg_logos, onLaterPages=draw_bg_logos)
