# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase.pdfmetrics import stringWidth
import datetime
 
AZUL   = colors.HexColor('#0d1b3e')
DORADO = colors.HexColor('#c9a227')
BLANCO = colors.white
GRIS   = colors.HexColor('#f5f5f5')
NEGRO  = colors.black
W, H   = letter  # 612 x 792 pts
 
LM = 15*mm
RM = 15*mm
TM = 10*mm
BM = 15*mm
TW = W - LM - RM   # usable width
 
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'logo_eshen.jpg')
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_eshen.jpg')
 
def ps(name, font='Helvetica', size=8, leading=10, color=NEGRO, align=TA_LEFT):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, alignment=align)
 
def S():
    return {
        'n'   : ps('n'),
        'b'   : ps('b',   font='Helvetica-Bold'),
        'wb'  : ps('wb',  font='Helvetica-Bold', color=BLANCO),
        'wbc' : ps('wbc', font='Helvetica-Bold', color=BLANCO, align=TA_CENTER),
        'th'  : ps('th',  font='Helvetica-Bold', size=11, leading=14, color=BLANCO, align=TA_CENTER),
        'sh'  : ps('sh',  font='Helvetica-Bold', size=9,  leading=11, color=BLANCO, align=TA_CENTER),
        'cn'  : ps('cn',  font='Helvetica-Bold', size=26, leading=30, color=DORADO, align=TA_CENTER),
        'co'  : ps('co',  font='Helvetica-Bold', size=8,  leading=10, color=NEGRO,  align=TA_CENTER),
        'gr'  : ps('gr',  font='Helvetica-Bold', size=9,  leading=12, color=DORADO, align=TA_CENTER),
        'ch'  : ps('ch',  font='Helvetica-Bold', size=8,  leading=10, color=DORADO, align=TA_CENTER),
        'mr'  : ps('mr',  size=8, leading=10, color=NEGRO, align=TA_RIGHT),
        'mbr' : ps('mbr', font='Helvetica-Bold', size=8, leading=10, color=NEGRO, align=TA_RIGHT),
        'fi'  : ps('fi',  font='Helvetica-Bold', size=8, leading=12, color=NEGRO, align=TA_CENTER),
        'no'  : ps('no',  font='Helvetica-Bold', size=8, leading=10, color=NEGRO),
        'c'   : ps('c',   size=8, leading=10, color=NEGRO, align=TA_CENTER),
        'cb'  : ps('cb',  font='Helvetica-Bold', size=8, leading=10, color=NEGRO, align=TA_CENTER),
        'wbr' : ps('wbr', font='Helvetica-Bold', size=8, leading=10, color=BLANCO, align=TA_RIGHT),
        'dr'  : ps('dr',  font='Helvetica-Bold', size=8, leading=10, color=DORADO, align=TA_RIGHT),
        'drl' : ps('drl', font='Helvetica-Bold', size=11, leading=13, color=DORADO, align=TA_RIGHT),
    }
 
def fm(v):
    try: return f'$ {float(v):,.2f}'
    except: return str(v)
 
def make_table(rows, col_widths, styles):
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle(styles))
    return t
 
def table_height(t, available_width):
    """Estimate table height by wrapping."""
    w, h = t.wrap(available_width, 9999)
    return h
 
def generar(data, out_path):
    styles = S()
    story_elements = []  # we'll collect (element, height) to calculate fill rows
 
    # -- PAGE SETUP ----------------------------------------------------------
    usable_h = H - TM - BM  # total vertical space
 
    # -- 1. HEADER -----------------------------------------------------------
    LOGO_W = 24*mm
    TXT_W  = TW - LOGO_W
 
    try:
        from reportlab.platypus import Image
        logo = Image(LOGO_PATH, width=LOGO_W-2*mm, height=LOGO_W-2*mm)
    except:
        logo = Paragraph('', styles['n'])
 
    hdr_inner = Table(
        [[Paragraph('COMERCIALIZADORA Y PRESTADORA DE SERVICIOS', styles['th'])],
         [Paragraph('INDUSTRIALES ESHEN', styles['sh'])]],
        colWidths=[TXT_W]
    )
    hdr_inner.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
 
    hdr = Table([[hdr_inner, logo]], colWidths=[TXT_W, LOGO_W])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(1,0),(1,0),'CENTER'),
        ('BOX',(0,0),(-1,-1),1.5,DORADO),
        ('TOPPADDING',(0,0),(-1,-1),3),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]))
 
    # -- 2. RFC / COT ROW ----------------------------------------------------
    COT_W  = 46*mm
    INFO_W = TW - COT_W
    IC     = [INFO_W*0.32, INFO_W*0.30, INFO_W*0.18, INFO_W*0.20]
 
    rfc_e  = data.get('rfc_emisor','')
    email_e= data.get('email_emisor','')
    prov   = data.get('proveedor','')
    fecha  = data.get('fecha', datetime.date.today().strftime('%d/%m/%Y'))
    num    = data.get('numero_cotizacion','---')
 
    info = Table([
        [Paragraph(f'<b>RFC:</b> {rfc_e}', styles['n']),
         Paragraph(f'<b>Proveedor:</b> {prov}', styles['n']),
         Paragraph('<b>Fecha:</b>', styles['n']),
         Paragraph(fecha, styles['n'])],
        [Paragraph(f'<b>Email:</b> {email_e}', styles['n']), '','',''],
    ], colWidths=IC)
    info.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('SPAN',(1,1),(3,1)),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),3),
    ]))
 
    cot_box = Table([
        [Paragraph('COTIZACIN', styles['wbc'])],
        [Paragraph(str(num), styles['cn'])],
    ], colWidths=[COT_W])
    cot_box.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),
        ('BOX',(0,0),(-1,-1),1,DORADO),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),
    ]))
 
    top = Table([[info, cot_box]], colWidths=[INFO_W, COT_W])
    top.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
    ]))
 
    # -- 3. DATOS CLIENTE ----------------------------------------------------
    banner = Table([[Paragraph('DATOS DEL CLIENTE', styles['wbc'])]], colWidths=[TW])
    banner.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AZUL),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]))
 
    c   = data.get('cliente',{})
    vig = data.get('vigencia','30 das')
    cp  = data.get('condiciones_pago',['','',''])
    if isinstance(cp,str): cp=[cp,'','']
    while len(cp)<3: cp.append('')
 
    CC = [24*mm, TW-24*mm-34*mm-38*mm, 34*mm, 38*mm]
    cli = Table([
        [Paragraph('<b>Razon Social:</b>',styles['b']),
         Paragraph(c.get('razon_social',''),styles['n']),
         Paragraph('<b>Vigencia</b>',styles['b']),
         Paragraph('<b>CONDICIONES DE PAGO</b>',styles['b'])],
        [Paragraph('<b>RFC:</b>',styles['b']),
         Paragraph(c.get('rfc',''),styles['n']),
         Paragraph(vig,styles['n']),
         Paragraph(cp[0],styles['n'])],
        [Paragraph('<b>Direccin:</b>',styles['b']),
         Paragraph(c.get('direccion',''),styles['n']),
         '', Paragraph(cp[1],styles['n'])],
        [Paragraph('<b>Correo:</b>',styles['b']),
         Paragraph(c.get('correo',''),styles['n']),
         '', Paragraph(cp[2],styles['n'])],
        [Paragraph('<b>Atencin:</b>',styles['b']),
         Paragraph(c.get('atencion',''),styles['n']),'',''],
    ], colWidths=CC)
    cli.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#cccccc')),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('SPAN',(2,2),(2,4)),
    ]))
 
    # -- 4. PARTIDAS TABLE ---------------------------------------------------
    CW = [13*mm, 14*mm, 17*mm,
          TW - 13*mm - 14*mm - 17*mm - 28*mm - 28*mm,
          28*mm, 28*mm]
 
    hdrs = ['PARTIDA','CANTIDAD','SKU','C O N C E P T O','PRECIO\nUNITARIO','TOTAL']
    rows = [[Paragraph(h, styles['ch']) for h in hdrs]]
    sty  = [
        ('BACKGROUND',(0,0),(-1,0),AZUL),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#aaaaaa')),
        ('BOX',(0,0),(-1,-1),0.8,NEGRO),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),
    ]
    ri = 1; subtotal = 0.0
 
    for item in data.get('partidas',[]):
        tipo = item.get('tipo','partida')
        if tipo == 'grupo':
            rows.append(['','','', Paragraph(item.get('titulo',''), styles['gr']),'',''])
            sty += [
                ('SPAN',(0,ri),(-1,ri)),
                ('BACKGROUND',(0,ri),(-1,ri),AZUL),
                ('TOPPADDING',(0,ri),(-1,ri),4),
                ('BOTTOMPADDING',(0,ri),(-1,ri),4),
            ]
            ri += 1
        else:
            cant   = float(item.get('cantidad',0) or 0)
            p_unit = float(item.get('precio_unitario',0) or 0)
            tot    = cant * p_unit
            subtotal += tot
            rows.append([
                Paragraph(str(item.get('numero','')), styles['cb']),
                Paragraph(str(item.get('cantidad','')), styles['c']),
                Paragraph(str(item.get('sku','')), styles['c']),
                Paragraph(item.get('concepto',''), styles['co']),
                Paragraph(fm(p_unit), styles['mr']),
                Paragraph(fm(tot), styles['mbr']),
            ])
            sty += [('BACKGROUND',(0,ri),(-1,ri), GRIS if ri%2==0 else BLANCO)]
            ri += 1
 
    data_rows = ri  # rows so far (header + partidas)
 
    # -- EXACT HEIGHT MEASUREMENT -----------------------------------------
    EMPTY_ROW_H = 18.0
 
    def _h(elem): _, hh = elem.wrap(TW, 9999); return hh
 
    # Measure every fixed element with actual content
    fixed_h = (_h(hdr) + _h(top) + _h(banner) + _h(cli))
 
    # Measure the current partida rows table (header + partidas, no totals yet)
    tmp_tbl = Table(rows, colWidths=CW)
    tmp_tbl.setStyle(TableStyle(sty))
    fixed_h += _h(tmp_tbl)
 
    # Add totals, nota, firma heights (fixed)
    # Totals: 3 rows  ~9.5pts each  55pts
    # Nota: ~18pts, Firma: ~84pts
    fixed_h += 55.0 + 18.0 + 84.0
 
    # Safety buffer: subtract 2 empty rows to prevent overflow
    remaining = usable_h - fixed_h - (2 * EMPTY_ROW_H)
    empty_rows_needed = max(0, int(remaining / EMPTY_ROW_H))
 
    for _ in range(empty_rows_needed):
        rows.append(['','','','','',''])
        sty += [('BACKGROUND',(0,ri),(-1,ri), GRIS if ri%2==0 else BLANCO)]
        ri += 1
 
    # -- TOTALES -------------------------------------------------------------
    iva_pct = float(data.get('iva_porciento',16))/100
    iva_val = subtotal * iva_pct
    total   = subtotal + iva_val
 
    for lbl, val, big in [
        ('Subtotal M.N.', subtotal, False),
        ('IVA',           iva_val,  False),
        ('Total M.N.',    total,    True),
    ]:
        rows.append(['','','','',
                     Paragraph(lbl,  styles['wbr']),
                     Paragraph(fm(val), styles['drl'] if big else styles['dr'])])
        sty += [
            ('BACKGROUND',(0,ri),(3,ri),BLANCO),
            ('BACKGROUND',(4,ri),(4,ri),AZUL),
            ('BACKGROUND',(5,ri),(5,ri),AZUL),
            ('ALIGN',(4,ri),(-1,ri),'RIGHT'),
            ('RIGHTPADDING',(5,ri),(5,ri),5),
            ('LEFTPADDING',(4,ri),(4,ri),3),
            ('TOPPADDING',(4,ri),(5,ri),4 if big else 3),
            ('BOTTOMPADDING',(4,ri),(5,ri),4 if big else 3),
        ]
        if big:
            sty += [('LINEABOVE',(4,ri),(5,ri),1,DORADO)]
        ri += 1
 
    final_tbl = Table(rows, colWidths=CW, repeatRows=1)
    final_tbl.setStyle(TableStyle(sty))
 
    # -- NOTA ----------------------------------------------------------------
    nota = data.get('nota','')
    nota_tbl = Table(
        [[Paragraph(f'<b>NOTA:</b> {nota}', styles['no'])]],
        colWidths=[TW]
    )
    nota_tbl.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),
    ]))
 
    # -- FIRMA ---------------------------------------------------------------
    fn = data.get('firma_nombre','Ing. Alberto Lpez Malvez')
    fc = data.get('firma_cargo','DIRECTOR GENERAL')
    firma_tbl = Table([
        [Paragraph('ATENTAMENTE', styles['fi'])],
        [Paragraph(fn,            styles['fi'])],
        [Paragraph(fc,            styles['fi'])],
    ], colWidths=[TW])
    firma_tbl.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,NEGRO),
        ('BACKGROUND',(0,0),(-1,-1),GRIS),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
 
    # -- ASSEMBLE STORY -------------------------------------------------------
    story = [hdr, top, banner, cli, final_tbl, nota_tbl, firma_tbl]
 
    # -- BORDER ON EVERY PAGE ------------------------------------------------
    def on_page(canv, doc):
        canv.saveState()
        canv.setStrokeColor(NEGRO)
        canv.setLineWidth(1)
        canv.rect(LM-3, BM-3, W-LM-RM+6, H-TM-BM+6)
        canv.restoreState()
 
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM, bottomMargin=BM
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'PDF generado: {out_path}')
 
 
if __name__ == '__main__':
    # Test con pocas partidas
    datos_pocos = {
        "rfc_emisor":"CPS240403132","email_emisor":"eshecompras@gmail.com",
        "proveedor":"999","fecha":"01/06/2026","numero_cotizacion":"157",
        "vigencia":"30 das","condiciones_pago":["50% anticipo","50% entrega",""],
        "iva_porciento":16,
        "cliente":{"razon_social":"DAYRON PADILLA","rfc":"","direccion":"",
            "correo":"","atencion":"DAYRON PADILLA"},
        "partidas":[
            {"tipo":"partida","numero":"1","cantidad":43,"sku":"",
             "concepto":"Pieza 1- placa 1/4\" 150mm x 200mm- 6 barrenos 14mm",
             "precio_unitario":155},
            {"tipo":"partida","numero":"2","cantidad":74,"sku":"",
             "concepto":"Pieza 2- placa 1/4\" 55mm x 80mm- 3 barrenos 14mm",
             "precio_unitario":38.13},
        ],
        "nota":"TIEMPO DE ENTREGA 3 DIAS HABILES",
        "firma_nombre":"Ing. Alberto Lopez Malvaez","firma_cargo":"DIRECTOR GENERAL"
    }
    generar(datos_pocos, '/tmp/test_pocos.pdf')
 
    # Test con muchas partidas
    datos_muchos = {
        "rfc_emisor":"CPS240403132","email_emisor":"eshecompras@gmail.com",
        "proveedor":"209887","fecha":"16/04/2026","numero_cotizacion":"152",
        "vigencia":"30 das","condiciones_pago":["%","%","%"],"iva_porciento":16,
        "cliente":{"razon_social":"CHEP DE MEXICO S.A. DE C.V.","rfc":"CME940118F7A",
            "direccion":"AV. JAVIER BARROS SIERA 495, PISO 12","correo":"compras@chep.com",
            "atencion":"ING. ALDO VALENCIA Y/O COMPRAS SMO"},
        "partidas":[
            {"tipo":"grupo","titulo":"FABRICACION NAIL ROLLER PLANTA SMO"},
            {"tipo":"partida","numero":"01","cantidad":4,"sku":"","concepto":"FABRICACION DE CONVEYOR DOBLE CADENA PASO 80","precio_unitario":337000},
            {"tipo":"partida","numero":"02","cantidad":4,"sku":"","concepto":"MOTORREDUCTOR 5HP 440VAC","precio_unitario":112279},
            {"tipo":"partida","numero":"03","cantidad":4,"sku":"","concepto":"TOPE NEUMATICO PARA PALLET","precio_unitario":35000},
            {"tipo":"partida","numero":"04","cantidad":4,"sku":"","concepto":"FABRICACION DE ESTRUCTURA SUPERIOR CON 3 RUEDAS METALICAS","precio_unitario":85000},
            {"tipo":"partida","numero":"05","cantidad":4,"sku":"","concepto":"INSTALACION NEUMATICA COMPLETA","precio_unitario":60000},
        ],
        "nota":"PRECIO NO INCLUYE FLETE",
        "firma_nombre":"Ing. Alberto Lpez Malvez","firma_cargo":"DIRECTOR GENERAL"
    }
    generar(datos_muchos, '/tmp/test_muchos.pdf'
