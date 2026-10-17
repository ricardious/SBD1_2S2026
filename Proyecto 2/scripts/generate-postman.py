"""Genera una coleccion portable v2.1 con aserciones y datos aislados del historico."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
specs = json.loads((root / 'src/entities/schema.json').read_text())
data = json.loads((root / 'data/historico.json').read_text())
base = '{{baseUrl}}'
run = '{{runId}}'
aux = '{{auxId}}'
pay2 = '{{payId}}'

def request(name, method, path, body=None, status=200, tests=None):
    raw = json.dumps(body, ensure_ascii=False, indent=2)
    for token in (run, aux, pay2):
        raw = raw.replace('"' + token + '"', token)
    req = {'method': method, 'header': [] if body is None else [{'key': 'Content-Type', 'value': 'application/json'}], 'url': base + path}
    if body is not None:
        req['body'] = {'mode': 'raw', 'raw': raw, 'options': {'raw': {'language': 'json'}}}
    checks = [f"pm.test('HTTP {status}', () => pm.response.to.have.status({status}));"] + (tests or [])
    return {'name': name, 'request': req, 'event': [{'listen': 'test', 'script': {'type': 'text/javascript', 'exec': checks}}]}

sale = lambda key: {'id_venta': key, 'fecha_venta': '2026-10-16T12:00:00', 'id_tienda': 1, 'id_empleado': 1, 'id_cliente': 1, 'id_estado_venta': 1}
product = lambda key: {'id_producto': key, 'nombre': 'Demo producto ' + key, 'descripcion': 'Datos para probar la API', 'id_categoria': 1, 'id_marca': 1}
catalog = lambda key: {'id_tienda': 1, 'id_producto': key, 'precio_vigente': 25, 'existencia_actual': 10}
detail = lambda venta, producto, cantidad: {'id_venta': venta, 'id_producto': producto, 'cantidad': cantidad, 'precio_unitario': 25, 'subtotal': cantidad * 25}
payment = lambda key, amount: {'id_pago': key, 'id_venta': run, 'id_metodo_pago': 1, 'monto': amount}

health = request('Iniciar ejecucion y comprobar conexion', 'GET', '/health')
health['event'].insert(0, {'listen': 'prerequest', 'script': {'type': 'text/javascript', 'exec': [
    "const id = 1500000000 + Math.floor(Math.random() * 100000000);",
    "pm.collectionVariables.set('runId', id);",
    "pm.collectionVariables.set('auxId', id + 1);",
    "pm.collectionVariables.set('payId', id + 2);",
]}})
setup = [health,
    request('Verificar carga historica', 'GET', '/admin/importacion', tests=["pm.test('9068 filas historicas', () => pm.expect(pm.response.json().detalle.filas).to.eql(9068));"]),
    request('Persona auxiliar', 'POST', '/persona', {'id_persona': aux, 'nombres': 'Auxiliar', 'apellidos': 'Postman', 'telefono': '12345678', 'correo': None, 'direccion': 'Centro', 'id_municipio': 1}, 201),
    request('Producto auxiliar', 'POST', '/producto', product(aux), 201),
    request('Venta auxiliar', 'POST', '/venta', sale(aux), 201),
]
crud = []
for spec in specs:
    table = spec['table']
    if table == 'estado_venta':
        crud.append({'name': table + ' (catalogo protegido)', 'description': 'Los tres estados son inmutables; el CRUD devuelve conflictos intencionales.', 'item': [
            request('Listar', 'GET', '/estado_venta'), request('Buscar', 'GET', '/estado_venta/1'),
            request('POST duplicado', 'POST', '/estado_venta', {'id_estado_venta': 1, 'nombre': 'REGISTRADA'}, 409),
            request('PUT protegido', 'PUT', '/estado_venta/1', {'nombre': 'REGISTRADA'}, 409),
            request('DELETE protegido', 'DELETE', '/estado_venta/1', status=409),
        ]})
        continue
    row = dict(data[table][0])
    for key in spec['keys']:
        row[key] = run
    if 'nombre' in row:
        row['nombre'] = 'Demo ' + table + ' ' + run
    if table == 'persona': row['correo'] = None
    if table in ('empleado', 'cliente'): row['id_persona'] = aux
    if table == 'cliente': row['numero_identificacion'] = 'DOC' + run
    if table == 'catalogo_producto': row = catalog(aux)
    if table == 'venta': row = sale(run)
    if table == 'detalle_venta': row = detail(aux, aux, 2)
    if table == 'pago': row = {'id_pago': run, 'id_venta': aux, 'id_metodo_pago': 1, 'monto': 20}
    path = '/' + table
    itempath = path + '/' + '/'.join(str(row[k]) for k in spec['keys'])
    field = next(k for k in row if k not in spec['keys'] and not k.startswith('id_'))
    update = {field: row[field]}
    if table == 'detalle_venta': update = {'cantidad': 3, 'subtotal': 75}
    if table == 'pago': update = {'monto': 50}
    steps = []
    if table == 'detalle_venta': steps.append(request('Preparar inventario auxiliar', 'POST', '/catalogo_producto', catalog(aux), 201))
    if table == 'pago': steps.append(request('Preparar detalle para abonos', 'POST', '/detalle_venta', detail(aux, aux, 2), 201))
    steps += [request('Crear', 'POST', path, row, 201), request('Listar', 'GET', path + '?limit=5&offset=0'),
              request('Buscar por clave', 'GET', itempath), request('Actualizar', 'PUT', itempath, update),
              request('Eliminar', 'DELETE', itempath, status=204), request('Confirmar eliminacion', 'GET', itempath, status=404)]
    crud.append({'name': table, 'item': steps})

cleanup = [request('Eliminar detalle auxiliar', 'DELETE', '/detalle_venta/' + aux + '/' + aux, status=204),
           request('Eliminar venta auxiliar', 'DELETE', '/venta/' + aux, status=204),
           request('Eliminar catalogo auxiliar', 'DELETE', '/catalogo_producto/1/' + aux, status=204),
           request('Eliminar producto auxiliar', 'DELETE', '/producto/' + aux, status=204),
           request('Eliminar persona auxiliar', 'DELETE', '/persona/' + aux, status=204)]
scenario = [
    request('Producto demostracion', 'POST', '/producto', product(run), 201),
    request('Inventario inicial 10', 'POST', '/catalogo_producto', catalog(run), 201),
    request('Venta registrada', 'POST', '/venta', sale(run), 201),
    request('Stock insuficiente: pedir 11', 'POST', '/detalle_venta', detail(run, run, 11), 400, ["pm.test('Mensaje del trigger', () => pm.expect(pm.response.json().error).to.eql('Stock insuficiente'));"]),
    request('Inventario sigue en 10', 'GET', '/catalogo_producto/1/' + run, tests=["pm.test('Rollback sin descuento', () => pm.expect(pm.response.json().existencia_actual).to.eql(10));"]),
    request('Venta valida: pedir 2', 'POST', '/detalle_venta', detail(run, run, 2), 201),
    request('Inventario reducido a 8', 'GET', '/catalogo_producto/1/' + run, tests=["pm.test('Descuento automatico', () => pm.expect(pm.response.json().existencia_actual).to.eql(8));"]),
    request('Primer abono 20', 'POST', '/pago', payment(run, 20), 201),
    request('Estado aun REGISTRADA', 'GET', '/venta/' + run, tests=["pm.test('Abono parcial', () => pm.expect(pm.response.json().estado).to.eql('REGISTRADA'));"]),
    request('Segundo abono 30', 'POST', '/pago', payment(pay2, 30), 201),
    request('Estado automatico PAGADA', 'GET', '/venta/' + run, tests=["pm.test('Pagada por el motor', () => pm.expect(pm.response.json().estado).to.eql('PAGADA'));", "pm.test('Saldo cero', () => pm.expect(pm.response.json().saldo_pendiente).to.eql(0));"]),
    request('Otra venta para anular', 'POST', '/venta', sale(aux), 201),
    request('Detalle para anular', 'POST', '/detalle_venta', detail(aux, run, 1), 201),
    request('Anular sin pagos', 'PUT', '/venta/' + aux, {'id_estado_venta': 3}),
    request('Inventario devuelto una vez', 'GET', '/catalogo_producto/1/' + run, tests=["pm.test('Devolucion de stock', () => pm.expect(pm.response.json().existencia_actual).to.eql(8));"]),
    request('Repetir anulacion rechazada', 'PUT', '/venta/' + aux, {'id_estado_venta': 3}, 409),
]
reports = [request('Vista ' + name, 'GET', '/reportes/' + name, tests=["pm.test('Reporte JSON', () => pm.expect(pm.response.json().data).to.be.an('array'));"]) for name in ['ventas-ubicacion', 'top-productos', 'saldos-pendientes']]
collection = {'info': {'name': 'Comercial La Estrella - Fase 2', 'description': 'Ejecutar completa despues de importar el historico. CRUD aislado para las 19 tablas, catalogo de estados protegido, triggers y vistas. Conserva ventas de demostracion. Toda escritura pasa por HTTP.', 'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
              'variable': [{'key': 'baseUrl', 'value': 'http://127.0.0.1:3000/api'}],
              'item': [{'name': '00 Preparacion', 'item': setup}, {'name': '01 CRUD por entidad', 'item': crud}, {'name': '02 Limpieza auxiliares', 'item': cleanup}, {'name': '03 Triggers', 'item': scenario}, {'name': '04 Vistas', 'item': reports}]}
(root / 'postman/ComercialLaEstrella.postman_collection.json').write_text(json.dumps(collection, ensure_ascii=False, indent=2) + '\n')
environment = {'name': 'Comercial La Estrella local', 'values': [{'key': 'baseUrl', 'value': 'http://127.0.0.1:3000/api', 'enabled': True}], '_postman_variable_scope': 'environment'}
(root / 'postman/local.postman_environment.json').write_text(json.dumps(environment, indent=2) + '\n')
# Coleccion separada: requiere escoger el archivo local en Postman y habilitar la ruta.
import_req = request('Importar historico original (una sola vez)', 'POST', '/admin/importacion', status=201)
import_req['request']['header'] = [{'key': 'Content-Type', 'value': 'application/json'}, {'key': 'X-Import-Key', 'value': '{{importKey}}'}]
import_req['request']['body'] = {'mode': 'file', 'file': {'src': '../data/historico.json'}}
import_collection = {'info': {'name': 'Carga inicial historica - ejecutar una vez', 'description': 'Activar IMPORT_ENABLED, definir importKey local y seleccionar data/historico.json como Body binary. Desactivar al terminar. No exportar la clave.', 'schema': collection['info']['schema']}, 'variable': [{'key': 'baseUrl', 'value': 'http://127.0.0.1:3000/api'}, {'key': 'importKey', 'value': ''}], 'item': [import_req]}
(root / 'postman/Importacion.postman_collection.json').write_text(json.dumps(import_collection, ensure_ascii=False, indent=2) + '\n')
print('Colecciones y entorno generados.')
