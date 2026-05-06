import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime

def format_minutes(minutes):
    if not minutes: return "Pendiente"
    h = int(minutes // 60)
    m = int(minutes % 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"

def generate_consolidated_invoice(output_path, client_name, date_range_str, services, iva_percentage):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=40, bottomMargin=30)
    Story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#2D6ADF'), spaceAfter=5, alignment=1)
    sub_title_style = ParagraphStyle('CustomSubTitle', parent=styles['Normal'], fontSize=11, textColor=colors.gray, spaceAfter=20, alignment=1)

    # Logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_ticket.png")
    if os.path.exists(logo_path):
        try:
            from reportlab.lib.utils import ImageReader
            img_reader = ImageReader(logo_path)
            mw, mh = img_reader.getSize()
            aspect = mh / float(mw)
            target_width = 150
            img = RLImage(logo_path, width=target_width, height=target_width * aspect)
            img.hAlign = 'CENTER'
            Story.append(img)
            Story.append(Spacer(1, 10))
        except Exception: pass

    Story.append(Paragraph("REPORTE CONSOLIDADO DE MONITOREO Y CUSTODIA", title_style))
    Story.append(Paragraph("KYATRACKER - SERVICIOS SATELITALES Y SEGURIDAD", sub_title_style))
    
    # Info
    info_data = [
        ["Cliente:", client_name],
        ["Periodo:", date_range_str],
        ["Fecha de Emisión:", datetime.datetime.now().strftime('%d/%m/%Y %H:%M')],
        ["Total de Rutas:", str(len(services))]
    ]
    t_info = Table(info_data, colWidths=[150, 350], hAlign='LEFT')
    t_info.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    Story.append(t_info)
    Story.append(Spacer(1, 15))

    # Table
    table_data = [["Unidad", "Operador", "Origen -> Destino", "Salida", "Llegada", "Tiempo", "Subtotal"]]
    subtotal = 0.0
    for s in services:
        st_str = s.start_time.strftime('%d/%m/%y %H:%M') if s.start_time else ""
        end_str = s.arrival_time.strftime('%d/%m/%y %H:%M') if s.arrival_time else "En ruta"
        dur = format_minutes(s.billed_minutes)
        cost = f"${s.total_cost:.2f}" if s.total_cost else "Pendiente"
        
        # We must use a Paragraph for Origin -> Destination and Operador because they might be long text
        p_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8)
        table_data.append([
            Paragraph(s.unit, p_style),
            Paragraph(s.operator, p_style),
            Paragraph(f"{s.origin} a {s.destination}", p_style),
            st_str,
            end_str,
            dur,
            cost
        ])
        if s.total_cost:
            subtotal += s.total_cost

    t_services = Table(table_data, colWidths=[50, 75, 125, 75, 75, 60, 80], hAlign='CENTER')
    t_services.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2D6ADF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    Story.append(t_services)
    Story.append(Spacer(1, 20))

    # Totals
    iva_amount = subtotal * (iva_percentage / 100.0)
    total_amount = subtotal + iva_amount

    totals_data = [
        ["Subtotal:", f"${subtotal:.2f} MXN"],
        [f"IVA ({iva_percentage}%):", f"${iva_amount:.2f} MXN"],
        ["TOTAL A PAGAR:", f"${total_amount:.2f} MXN"]
    ]
    t_totals = Table(totals_data, colWidths=[350, 190], hAlign='CENTER')
    t_totals.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-2), 'Helvetica'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#DBEAFE')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    Story.append(t_totals)

    doc.build(Story)
