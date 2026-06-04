# -*- coding: utf-8 -*-
"""
Generador de Remision ESHEN
Pagina 1 (frente): 2 remisiones separadas por linea de corte
Pagina 2 (reverso): imagen de evidencia duplicada a la misma altura
"""
import os, base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph, Image, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas
import datetime
 
AZUL   = colors.HexColor('#0d1b3e')
DORADO = colors.HexColor('#c9a227')
BLANCO = colors.white
GRIS   = colors.HexColor('#f0f0f0')
NEGRO  = colors.black
W, H   = letter  # 612 x 792 pts
 
LM = 12*mm
RM = 12*mm
TM = 8*mm
BM = 8*mm
TW = W - LM - RM
 
MID_Y  = H / 2
HALF_H = MID_Y - BM - 4
 
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'logo_eshen.jpg')
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_eshen.jpg')
 
EMPRESA_NOMBRE  = 'COMERCIALIZADORA Y PRESTADORA DE SERVICIOS INDUSTRIALES ESHEN'
EMPRESA_CALLE   = 'CALLE FERNANDO MONTES DE OCA No. 21 INT. 12, COL. SAN NICOLAS'
EMPRESA_CIUDAD  = 'TLALNEPANTLA DE BAZ, EDO. DE MEX.  CP 54030'
EMPRESA_RFC_TEL = 'RFC: CPS-240403-132    TEL: (55) 90-79-67-52'
 
def ps(name, font='Helvetica', size=7, leading=9, color=NEGRO, align=TA_LEFT):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, alignment=align)
 
def fm(v):
    try: return '$ {:,.2f}'.format(float(v))
    except: return ''
 
def _h(elem, width=None):
    _, hh = elem.wrap(width or TW, 9999)
    return hh
 
def build_remision_story(data, sello_path=None):
    S = {
        'n'  : ps('n'),
        'b'  : ps('b',   font='Helvetica-Bold'),
        'bc' : ps('bc',  font='Helvetica-Bold', align=TA_CENTER),
        'c'  : ps('c',   align=TA_CENTER),
        'wbc': ps('wbc', font='Helvetica-Bold', color=BLANCO, align=TA_CENTER),
        'th' : ps('th',  font='Helvetica-Bold', size=9,  leading=11, color=AZUL, align=TA_CENTER),
        'sh' : ps('sh',  font='Helvetica-Bold', size=6.5,leading=8,  color=NEGRO, align=TA_CENTER),
        'cn' : ps('cn',  font='Helvetica-Bold', size=20, leading=24, color=DORADO, align=TA_CENTER),
        'ch' : ps('ch',  font='Helvetica-Bold', size=7,  leading=9,  color=DORADO, align=TA_CENTER),
        'mr' : ps('mr',  size=7, leading=9, color=NEGRO, align=TA_RIGHT),
        'mbr': ps('mbr', font='Helvetica-Bold', size=7, leading=9, color=NEGRO, align=TA_RIGHT),
        'co' : ps('co',  font='Helvetica-Bold', size=7, leading=9, color=NEGRO, align=TA_CENTER),
        'no' : ps('no',  font='Helvetica-Bold', size=7, leading=9, color=NEGRO),
        'fi' : ps('fi',  font='Helvetica-Bold', size=7, leading=10, color=NEGRO, align=TA_CENTER),
        'dr' : ps('dr',  font='Helvetica-Bold', size=7, leading=9,  color=DORADO, align=TA_RIGHT),
        'drl': ps('drl', font='Helvetica-Bold', size=9, leading=11, color=DORADO, align=TA_RIGHT),
        'wbr': ps('wbr', font='Helvetica-Bold', size=7, leading=9,  color=BLANCO, align=TA_RIGHT),
    }
    story = []
 
    LOGO_W = 20*mm; TXT_W = TW - LOGO_W
    try:    logo = Image(LOGO_PATH, width=LOGO_W-1*mm, height=LOGO_W-1*mm)
    except: logo = Paragraph('ESHEN', S['wbc'])
 
    hdr_inner = Table([
        [Paragraph(EMPRESA_NOMBRE,  S['th'])],
        [Paragraph(EMPRESA_CALLE,   S['sh'])],
        [Paragraph(EMPRESA_CIUDAD,  S['sh'])],
        [Paragraph(EMPRESA_RFC_TEL, S['sh'])],
    ], colWidths=[TXT_W])
    hdr_inner.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BLANCO),
        ('TOPPADDING',(0,0),(-1,-1),1.5),('BOTTOMPADDING',(0,0),(-1,-1),1.5),
        ('LEFTPADDING',(0,0),(-1,-1),4),
    ]))
    hdr = Table([[hdr_inner, logo]], colWidths=[TXT_W, LOGO_W])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BLANCO),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(1,0),(1,0),'CENTER'),
        ('BOX',(0,0),(-1,-1),1.5,NEGRO),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))
    story.append(hdr)
 
    num   = data.get('numero_remision', data.get('numero_cotizacion','---'))
    fecha = data.get('fecha', datetime.date.today().strftime('%d/%m/%Y'))
    rfc_e = data.get('rfc_emisor','')
    prov  = data.get('proveedor','')
 
    REM_W = 36*mm; INFO_W = TW - REM_W
    IC = [INFO_W*0.35, INFO_W*0.35, INFO_W*0.15, INFO_W*0.15]
    info = Table([[
        Paragraph('<b>RFC:</b> ' + rfc_e, S['n']),
        Paragraph('<b>Proveedor:</b> ' + prov, S['n']),
        Paragraph('<b>Fecha:</b>', S['n']),
        Paragraph(fecha, S['n']),
    ]], colWidths=IC)
    info.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),3),
    ]))
    rem_box = Table([
        [Paragraph('REMISION', S['wbc'])],
        [Paragraph(str(num), S['cn'])],
    ], colWidths=[REM_W])
    rem_box.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),('BOX',(0,0),(-1,-1),1,DORADO),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))
    top = Table([[info, rem_box]], colWidths=[INFO_W, REM_W])
    top.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),0.5,NEGRO)]))
    story.append(top)
 
    banner = Table([[Paragraph('DATOS DEL CLIENTE', S['wbc'])]], colWidths=[TW])
    banner.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AZUL),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    story.append(banner)
 
    c  = data.get('cliente', {})
    CC = [20*mm, TW-20*mm-28*mm-32*mm, 28*mm, 32*mm]
    cli = Table([
        [Paragraph('<b>Razon Social:</b>',S['b']), Paragraph(c.get('razon_social',''),S['n']),
         Paragraph('<b>RFC:</b>',S['b']), Paragraph(c.get('rfc',''),S['n'])],
        [Paragraph('<b>Domicilio:</b>',S['b']), Paragraph(c.get('direccion',''),S['n']),
         Paragraph('<b>Contacto:</b>',S['b']), Paragraph(c.get('atencion',''),S['n'])],
    ], colWidths=CC)
    cli.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),3),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(cli)
 
    CW = [10*mm, 12*mm, TW-10*mm-12*mm-22*mm-22*mm, 22*mm, 22*mm]
    hdrs = ['PARTIDA','CANT.','C O N C E P T O','P. UNITARIO','TOTAL']
    rows = [[Paragraph(h, S['ch']) for h in hdrs]]
    sty  = [
        ('BACKGROUND',(0,0),(-1,0),AZUL),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#aaaaaa')),
        ('BOX',(0,0),(-1,-1),0.8,NEGRO),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),
    ]
    ri = 1; subtotal = 0.0
 
    for item in data.get('partidas', []):
        if item.get('tipo') == 'grupo':
            rows.append(['','', Paragraph(item.get('titulo',''), S['bc']),'',''])
            sty += [('SPAN',(0,ri),(-1,ri)),('BACKGROUND',(0,ri),(-1,ri),AZUL),
                    ('TOPPADDING',(0,ri),(-1,ri),3),('BOTTOMPADDING',(0,ri),(-1,ri),3)]
            ri += 1
        elif item.get('tipo') == 'partida':
            cant   = float(item.get('cantidad',0) or 0)
            p_unit = float(item.get('precio_unitario',0) or 0)
            tot    = cant * p_unit; subtotal += tot
            rows.append([
                Paragraph(str(item.get('numero','')),   S['bc']),
                Paragraph(str(item.get('cantidad','')), S['c']),
                Paragraph(item.get('concepto',''),      S['co']),
                Paragraph(fm(p_unit), S['mr']),
                Paragraph(fm(tot),    S['mbr']),
            ])
            sty += [('BACKGROUND',(0,ri),(-1,ri), GRIS if ri%2==0 else BLANCO)]
            ri += 1
 
    fixed_h_so_far = sum(_h(e) for e in story)
    tmp = Table(rows, colWidths=CW); tmp.setStyle(TableStyle(sty))
    EMPTY_H = 14.0
    used = fixed_h_so_far + _h(tmp) + 42.0 + 14.0 + 30.0 + 4
    avail = HALF_H - used
    n_empty = max(0, int(avail / EMPTY_H) - 1)
 
    for _ in range(n_empty):
        rows.append(['','','','',''])
        sty += [('BACKGROUND',(0,ri),(-1,ri), GRIS if ri%2==0 else BLANCO)]
        ri += 1
 
    iva_pct = float(data.get('iva_porciento',16))/100
    iva_val = subtotal * iva_pct; total = subtotal + iva_val
    for lbl, val, big in [('Sub-Total',subtotal,False),('I.V.A.',iva_val,False),('TOTAL',total,True)]:
        rows.append(['','','', Paragraph(lbl, S['wbr']), Paragraph(fm(val), S['drl'] if big else S['dr'])])
        sty += [
            ('BACKGROUND',(0,ri),(2,ri),BLANCO),('BACKGROUND',(3,ri),(4,ri),AZUL),
            ('ALIGN',(3,ri),(4,ri),'RIGHT'),('RIGHTPADDING',(4,ri),(4,ri),4),
            ('TOPPADDING',(3,ri),(4,ri),3 if not big else 4),
            ('BOTTOMPADDING',(3,ri),(4,ri),3 if not big else 4),
        ]
        if big: sty += [('LINEABOVE',(3,ri),(4,ri),1,DORADO)]
        ri += 1
 
    tbl = Table(rows, colWidths=CW, repeatRows=1)
    tbl.setStyle(TableStyle(sty))
    story.append(tbl)
 
    nota = data.get('nota','')
    nota_row = Table([[
        Paragraph('<b>NOTA:</b> ' + nota, S['no']),
        Paragraph('"ESTE DOCUMENTO NO TIENE VALOR FISCAL"', S['bc']),
    ]], colWidths=[TW*0.55, TW*0.45])
    nota_row.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),4),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(nota_row)
 
    SELLO_W = 45*mm
    fn = data.get('firma_nombre','Ing. Alberto Lopez Malvaez')
    fc = data.get('firma_cargo','DIRECTOR GENERAL')
 
    firma_txt = Table([
        [Paragraph('ENTREGUE CONFORME', S['fi'])],
        [Paragraph('_______________________', S['fi'])],
        [Paragraph(fn, S['fi'])],
        [Paragraph(fc, S['fi'])],
    ], colWidths=[TW - SELLO_W])
    firma_txt.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),('BACKGROUND',(0,0),(-1,-1),GRIS),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
 
    if sello_path and os.path.exists(sello_path):
        try:
            sello_cell = Image(sello_path, width=SELLO_W-4*mm, height=26*mm)
        except:
            sello_cell = None
    else:
        sello_cell = None
 
    if sello_cell is None:
        sello_cell = Table([
            [Paragraph('RECIBI CONFORME', S['fi'])],
            [Paragraph('', S['fi'])],
            [Paragraph('_________________', S['fi'])],
            [Paragraph('SELLO / FIRMA', S['fi'])],
        ], colWidths=[SELLO_W])
        sello_cell.setStyle(TableStyle([
            ('BOX',(0,0),(-1,-1),0.8,NEGRO),('BACKGROUND',(0,0),(-1,-1),BLANCO),
            ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
 
    firma_row = Table([[firma_txt, sello_cell]], colWidths=[TW-SELLO_W, SELLO_W])
    firma_row.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
    ]))
    story.append(firma_row)
    return story
 
 
def build_evidencia_block(evidencia_path, label=''):
    S_bc = ParagraphStyle('ebc', fontName='Helvetica-Bold', fontSize=7, leading=9,
                          textColor=NEGRO, alignment=TA_CENTER)
    S_wb = ParagraphStyle('ewb', fontName='Helvetica-Bold', fontSize=8, leading=10,
                          textColor=BLANCO, alignment=TA_CENTER)
    story = []
 
    banner = Table([[Paragraph('EVIDENCIA / COMPROBANTE DE ENTREGA', S_wb)]], colWidths=[TW])
    banner.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),('BOX',(0,0),(-1,-1),1,DORADO),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(banner)
 
    if label:
        lbl_tbl = Table([[Paragraph(label, S_bc)]], colWidths=[TW])
        lbl_tbl.setStyle(TableStyle([
            ('BOX',(0,0),(-1,-1),0.5,NEGRO),
            ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ]))
        story.append(lbl_tbl)
        banner_h = _h(banner) + _h(lbl_tbl)
    else:
        banner_h = _h(banner)
 
    img_max_h = HALF_H - banner_h - 8
    img_max_w = TW
 
    if evidencia_path and os.path.exists(evidencia_path):
        try:
            from PIL import Image as PILImage
            pil = PILImage.open(evidencia_path)
            orig_w, orig_h = pil.size
            ratio = min(img_max_w / orig_w, img_max_h / orig_h)
            img_w = orig_w * ratio
            img_h = orig_h * ratio
            img = Image(evidencia_path, width=img_w, height=img_h)
            img_tbl = Table([[img]], colWidths=[TW])
            img_tbl.setStyle(TableStyle([
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('TOPPADDING',(0,0),(-1,-1),4),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ]))
            story.append(img_tbl)
        except Exception as e:
            msg = Table([[Paragraph('Error al cargar imagen: ' + str(e), S_bc)]], colWidths=[TW])
            story.append(msg)
    else:
        ph = Table([
            [Paragraph('[ Cargar imagen de evidencia desde el cotizador ]', S_bc)],
        ], colWidths=[TW])
        ph.setStyle(TableStyle([
            ('BOX',(0,0),(-1,-1),1,colors.HexColor('#cccccc')),
            ('BACKGROUND',(0,0),(-1,-1),GRIS),
            ('TOPPADDING',(0,0),(-1,-1),img_max_h/2-10),
            ('BOTTOMPADDING',(0,0),(-1,-1),img_max_h/2-10),
        ]))
        story.append(ph)
 
    return story
 
 
def generar_remision(data, out_path, sello_path=None, evidencia_path=None):
    c = pdfcanvas.Canvas(out_path, pagesize=letter)
    num = data.get('numero_remision', data.get('numero_cotizacion',''))
    c.setTitle('Remision ' + str(num))
 
    def draw_page_decor():
        c.saveState()
        c.setStrokeColor(NEGRO); c.setLineWidth(1)
        c.rect(LM-3, BM-3, W-LM-RM+6, H-TM-BM+6)
        c.setLineWidth(0.6); c.setDash(4, 3)
        c.line(LM, MID_Y, W-RM, MID_Y)
        c.setDash()
        c.setFont('Helvetica', 7)
        c.drawString(LM+4, MID_Y+2, '--- Recortar aqui / Cut here ---')
        c.restoreState()
 
    # PAGINA 1: FRENTE
    frame_top = Frame(LM, MID_Y+3, TW, HALF_H,
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0, showBoundary=0)
    frame_top.addFromList(build_remision_story(data, sello_path), c)
 
    frame_bot = Frame(LM, BM+2, TW, HALF_H,
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0, showBoundary=0)
    frame_bot.addFromList(build_remision_story(data, sello_path), c)
 
    draw_page_decor()
    c.showPage()
 
    # PAGINA 2: REVERSO
    label = 'Remision {}  |  {}  |  {}'.format(
        num,
        data.get('cliente',{}).get('razon_social',''),
        data.get('fecha','')
    )
 
    frame_rev_top = Frame(LM, MID_Y+3, TW, HALF_H,
                          leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0, showBoundary=0)
    frame_rev_top.addFromList(build_evidencia_block(evidencia_path, label), c)
 
    frame_rev_bot = Frame(LM, BM+2, TW, HALF_H,
                          leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0, showBoundary=0)
    frame_rev_bot.addFromList(build_evidencia_block(evidencia_path, label), c)
 
    c.saveState()
    c.setStrokeColor(NEGRO); c.setLineWidth(1)
    c.rect(LM-3, BM-3, W-LM-RM+6, H-TM-BM+6)
    c.setLineWidth(0.6); c.setDash(4, 3)
    c.line(LM, MID_Y, W-RM, MID_Y)
    c.setDash()
    c.restoreState()
 
    c.showPage()
    c.save()
    print('Remision generada: ' + out_path)
