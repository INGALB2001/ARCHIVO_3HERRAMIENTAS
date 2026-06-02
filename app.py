import os, sys, io, tempfile, base64
from flask import Flask, send_from_directory, request, send_file
 
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from generar_pdf import generar
from generar_remision import generar_remision
 
app = Flask(__name__, static_folder='static', static_url_path='/static')
 
@app.route('/')
def home():
    return send_from_directory(BASE, 'panel.html')
 
@app.route('/laser')
def laser():
    return send_from_directory(BASE, 'laser.html')
 
@app.route('/cotizador')
def cotizador_page():
    return send_from_directory(BASE, 'cotizador.html')
 
@app.route('/remision')
def remision_page():
    return send_from_directory(BASE, 'remision.html')
 
@app.route('/generar', methods=['POST'])
def gen_pdf():
    data = request.get_json(force=True)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        path = tmp.name
    generar(data, path)
    with open(path, 'rb') as f:
        buf = io.BytesIO(f.read())
    os.unlink(path)
    buf.seek(0)
    num = data.get('numero_cotizacion', 'ESHEN')
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True, download_name='COT_{}.pdf'.format(num))
 
@app.route('/generar-remision', methods=['POST'])
def gen_remision():
    data = request.get_json(force=True)
    sello_path = evidencia_path = None
    temps = []
 
    def save_b64(b64_str, mime):
        ext = '.jpg' if 'jpeg' in mime or 'jpg' in mime else '.png'
        raw = base64.b64decode(b64_str)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as t:
            t.write(raw); return t.name
 
    if data.get('sello_b64'):
        sello_path = save_b64(data['sello_b64'], data.get('sello_mime','image/jpeg'))
        temps.append(sello_path)
    if data.get('evidencia_b64'):
        evidencia_path = save_b64(data['evidencia_b64'], data.get('evidencia_mime','image/jpeg'))
        temps.append(evidencia_path)
 
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        out_path = tmp.name
    temps.append(out_path)
 
    try:
        generar_remision(data, out_path, sello_path=sello_path, evidencia_path=evidencia_path)
        with open(out_path, 'rb') as f:
            buf = io.BytesIO(f.read())
        buf.seek(0)
        num = data.get('numero_remision', data.get('numero_cotizacion', 'ESHEN'))
        return send_file(buf, mimetype='application/pdf',
                         as_attachment=True, download_name='REM_{}.pdf'.format(num))
    finally:
        for p in temps:
            if p and os.path.exists(p):
                try: os.unlink(p)
                except: pass
 
@app.route('/health')
def health():
    return {'status': 'ok'}
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print('\n  Panel Industrial listo en http://localhost:{}\n'.format(port))
    app.run(host='0.0.0.0', port=port, debug=False)
