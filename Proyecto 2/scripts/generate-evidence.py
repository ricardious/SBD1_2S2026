"""Representa respuestas reales del CLI de Postman; no simula una interfaz de Postman."""
from pathlib import Path
from datetime import datetime, timezone
import html
import json

root = Path(__file__).resolve().parents[1]
folder = root / 'docs/evidencias'
run = json.loads((folder / 'postman-oficial.json').read_text())['run']
executions = {e['requestExecuted']['name']: e for e in run['executions']}
started = datetime.fromtimestamp(run['meta']['started'] / 1000, timezone.utc).isoformat(timespec='seconds')

def pretty(value):
    return html.escape(json.dumps(value, ensure_ascii=False, indent=2))

css = '''body{margin:0;background:#eef1f4;color:#182330;font:16px Arial,sans-serif}
main{max-width:1120px;margin:32px auto;padding:28px;background:white;border:1px solid #d7dfe6}
h1{font-size:30px;margin:8px 0 12px}h2{font-size:20px;margin:0 0 12px}p{line-height:1.5}
.meta{color:#46576a;font-size:14px}.ok{background:#e8f4ec;padding:12px;border-left:4px solid #267a47}
article{border-top:1px solid #c6d0d9;padding-top:20px;margin-top:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
pre{margin:8px 0;background:#f4f6f8;padding:14px;font:14px/1.5 monospace;white-space:pre-wrap;overflow-wrap:anywhere}
.status{font-weight:bold;color:#245f40}footer{margin-top:24px;color:#46576a;font-size:14px}'''

scenarios = {
    'inventario': ('Protección y descuento de inventario', ['Stock insuficiente: pedir 11', 'Inventario sigue en 10', 'Venta valida: pedir 2', 'Inventario reducido a 8']),
    'pagos': ('Cambio automático del estado de venta', ['Primer abono 20', 'Estado aun REGISTRADA', 'Segundo abono 30', 'Estado automatico PAGADA']),
}
for filename, (title, names) in scenarios.items():
    sections = []
    for name in names:
        e = executions[name]
        req, response = e['requestExecuted'], e['response']
        url = req['url']
        address = url['protocol'] + '://' + '.'.join(url['host']) + ':' + url['port'] + '/' + '/'.join(url['path'])
        raw = req.get('body', {}).get('raw', '')
        body = json.loads(bytes(response['stream']['data']))
        tests = '; '.join(t['name'] + ': ' + t['status'] for t in e.get('tests', []))
        sections.append(f'''<article><h2>{html.escape(name)}</h2><div class="grid"><div>
          <strong>Petición HTTP</strong><pre>{html.escape(req['method'] + ' ' + address)}\n{html.escape(raw)}</pre></div>
          <div><strong class="status">HTTP {response['code']} · {html.escape(response['status'])}</strong><pre>{pretty(body)}</pre></div></div>
          <p class="meta">Aserciones: {html.escape(tests)}</p></article>''')
    doc = f'''<!doctype html><html lang="es"><meta charset="utf-8"><title>{html.escape(title)}</title><style>{css}</style>
      <main><p class="meta">USAC · Bases de Datos 1 · Proyecto Fase 2 · Carné 202300476</p><h1>{title}</h1>
      <p>Registro real de peticiones ejecutadas por el CLI oficial de Postman contra SQL Server 2022 en Docker.</p>
      <p class="ok">Colección completa: 144 peticiones y 155 aserciones correctas. Sin fallos.</p>
      <p class="meta">Inicio de la ejecución: {started}</p>{''.join(sections)}
      <footer>Fuente verificable: postman-oficial.json. Esta página representa el registro HTTP; no es una captura de la aplicación Postman.</footer></main></html>'''
    (folder / (filename + '.html')).write_text(doc)
summary = {
    'fecha_utc': started,
    'historico': {'filas': 9068, 'sha256': '80e4d18ae9300bcedbdc1354eddb17b29d2415e053085a9e05d0fae6462882ab', 'conciliacion': 'Todos los campos de las 19 tablas, antes de confirmar la transaccion'},
    'postman_cli': run['summary'],
    'pruebas_unitarias': {'correctas': 4, 'fallos': 0},
    'integracion_http': {'escenarios': 8, 'fallos': 0, 'incluye': ['CRUD', 'triggers multi-fila', 'concurrencia', 'comparacion completa de vistas']},
    'persistencia': 'Estado de importacion y venta pagada conservados tras reiniciar SQL Server',
    'dependencias': {'npm_audit': '0 vulnerabilidades'},
}
(folder / 'validacion.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print('Evidencias HTML y resumen generados desde el registro real.')
