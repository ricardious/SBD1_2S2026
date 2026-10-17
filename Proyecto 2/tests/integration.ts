import 'dotenv/config';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';

const base = process.env.API_URL ?? 'http://127.0.0.1:3000/api';
const id = 1000000000 + Math.floor(Date.now() / 1000) % 900000000;
const proof: object[] = [];
async function request(method: string, path: string, body?: unknown, expected = 200, headers: Record<string, string> = {}) {
  const response = await fetch(base + path, { method, headers: { 'Content-Type': 'application/json', ...headers }, body: body === undefined ? undefined : JSON.stringify(body) });
  const value = response.status === 204 ? null : await response.json();
  assert.equal(response.status, expected, `${method} ${path}: ${JSON.stringify(value)}`);
  const captured = value?.data && Array.isArray(value.data) && value.data.length > 5
    ? { ...value, data: value.data.slice(0, 3), filas_en_respuesta: value.data.length, muestra: true } : value;
  proof.push({ method, path, status: response.status, response: captured });
  return value;
}
const sale = (n: number) => ({ id_venta: id + n, fecha_venta: '2026-10-16T12:00:00', id_tienda: id, id_empleado: id, id_cliente: id, id_estado_venta: 1 });
const detail = (n: number, amount: number, product = id) => ({ id_venta: id + n, id_producto: product, cantidad: amount, precio_unitario: 25, subtotal: amount * 25 });
const stock = async (product = id) => (await request('GET', `/catalogo_producto/${id}/${product}`)).existencia_actual;

test('integracion real por HTTP: historico, CRUD, triggers, concurrencia y vistas', { timeout: 240000 }, async t => {
  await request('GET', '/health');
  await t.test('historico protegido y conciliado', async () => {
    const status = await request('GET', '/admin/importacion');
    assert.equal(status.importado, true, 'Ejecute npm run import:historico primero');
    assert.equal(status.detalle.filas, 9068);
    await request('POST', '/admin/importacion', {}, status.habilitada ? 401 : 404);
    await request('POST', '/admin/importacion', {}, status.habilitada ? 400 : 404, { 'X-Import-Key': process.env.IMPORT_KEY! });
    const original = JSON.parse(await readFile('data/historico.json', 'utf8'));
    await request('POST', '/admin/importacion', original, status.habilitada ? 409 : 404, { 'X-Import-Key': process.env.IMPORT_KEY! });
    const manifest = JSON.parse(await readFile('data/manifest.json', 'utf8'));
    for (const [table, count] of Object.entries(manifest.counts)) {
      const listing = await request('GET', `/${table}?limit=1`);
      assert.ok(listing.total >= Number(count), table);
    }
  });
  await t.test('CRUD de catalogos y entidades relacionadas', async () => {
    const records: [string, Record<string, any>][] = [
      ['pais', { id_pais: id, nombre: `QA pais ${id}` }],
      ['departamento', { id_departamento: id, nombre: `QA departamento ${id}`, id_pais: id }],
      ['municipio', { id_municipio: id, nombre: `QA municipio ${id}`, id_departamento: id }],
      ['tipo_tienda', { id_tipo_tienda: id, nombre: `QA tipo ${id}` }],
      ['tipo_identificacion', { id_tipo_identificacion: id, nombre: `QA identificacion ${id}` }],
      ['cargo', { id_cargo: id, nombre: `QA cargo ${id}` }],
      ['categoria', { id_categoria: id, nombre: `QA categoria ${id}` }],
      ['marca', { id_marca: id, nombre: `QA marca ${id}` }],
      ['metodo_pago', { id_metodo_pago: id, nombre: `QA metodo ${id}` }],
      ['persona', { id_persona: id, nombres: 'QA', apellidos: 'Empleado', telefono: '12345678', correo: null, direccion: 'Centro', id_municipio: id }],
      ['tienda', { id_tienda: id, nombre: `QA tienda ${id}`, direccion: 'Centro', telefono: '12345678', id_municipio: id, id_tipo_tienda: id }],
      ['empleado', { id_empleado: id, fecha_contratacion: '2026-01-01', id_tienda: id, id_cargo: id, id_persona: id }],
      ['cliente', { id_cliente: id, id_tipo_identificacion: id, numero_identificacion: `QA${id}`, id_persona: id }],
      ['producto', { id_producto: id, nombre: `QA producto ${id}`, descripcion: 'Prueba de inventario', id_categoria: id, id_marca: id }],
    ];
    for (const [table, record] of records) {
      await request('POST', `/${table}`, record, 201);
      await request('GET', `/${table}/${id}`);
      const field = table === 'persona' ? 'nombres' : table === 'empleado' ? 'fecha_contratacion' : table === 'cliente' ? 'numero_identificacion' : 'nombre';
      const value = field === 'fecha_contratacion' ? '2026-01-02' : `${record[field]} editado`;
      await request('PUT', `/${table}/${id}`, { [field]: value });
      await request('GET', `/${table}?limit=1`);
      // Probar DELETE exitoso con una segunda fila sin referencias.
      const temporary = { ...record };
      const key = Object.keys(record)[0];
      temporary[key] = id + 50;
      if (typeof temporary.nombre === 'string') temporary.nombre += ' temporal';
      if (table === 'empleado' || table === 'cliente') {
        await request('POST', '/persona', { id_persona: id + 50, nombres: 'Temporal', apellidos: table, telefono: '123', correo: null, direccion: 'Centro', id_municipio: id }, 201);
        temporary.id_persona = id + 50;
        if (table === 'cliente') temporary.numero_identificacion += 'T';
      }
      await request('POST', `/${table}`, temporary, 201);
      await request('DELETE', `/${table}/${id + 50}`, undefined, 204);
      if (table === 'empleado' || table === 'cliente') await request('DELETE', `/persona/${id + 50}`, undefined, 204);
    }
    await request('POST', '/estado_venta', { id_estado_venta: 1, nombre: 'REGISTRADA' }, 409);
    await request('GET', '/estado_venta/1');
    await request('PUT', '/estado_venta/1', { nombre: 'REGISTRADA' }, 409);
    await request('DELETE', '/estado_venta/1', undefined, 409);
    await request('POST', '/pais', { id_pais: id, nombre: 'duplicado' }, 409);
    await request('DELETE', `/pais/${id}`, undefined, 409);
    await request('GET', '/pais/2147483647', undefined, 404);
    await request('POST', '/pais', { id_pais: id + 51, nombre: 'x', extra: true }, 400);
    await request('GET', '/pais?limit=501', undefined, 400);
    await request('POST', '/catalogo_producto', { id_tienda: id, id_producto: id, precio_vigente: 25, existencia_actual: 10 }, 201);
    await request('PUT', `/catalogo_producto/${id}/${id}`, { precio_vigente: 26 });
    await request('DELETE', `/catalogo_producto/${id}/${id}`, undefined, 204);
    await request('POST', '/catalogo_producto', { id_tienda: id, id_producto: id, precio_vigente: 25, existencia_actual: 10 }, 201);
    await request('POST', '/producto', { id_producto: id + 1, nombre: `QA segundo ${id}`, descripcion: 'Otro producto', id_categoria: id, id_marca: id }, 201);
    await request('POST', '/catalogo_producto', { id_tienda: id, id_producto: id + 1, precio_vigente: 25, existencia_actual: 10 }, 201);
    await request('POST', '/venta', sale(50), 201);
    await request('PUT', `/venta/${id + 50}`, { fecha_venta: '2026-10-16T13:00:00' });
    await request('DELETE', `/venta/${id + 50}`, undefined, 204);
  });
  await t.test('stock insuficiente revierte; UPDATE y DELETE ajustan diferencias', async () => {
    await request('POST', '/venta', sale(0), 201);
    const failure = await request('POST', '/detalle_venta', detail(0, 11), 400);
    assert.equal(failure.error, 'Stock insuficiente');
    assert.equal(await stock(), 10);
    await request('GET', `/detalle_venta/${id}/${id}`, undefined, 404);
    await request('POST', '/detalle_venta', detail(0, 2), 201);
    assert.equal(await stock(), 8);
    await request('PUT', `/detalle_venta/${id}/${id}`, { cantidad: 3, subtotal: 75 });
    assert.equal(await stock(), 7);
    await request('PUT', `/detalle_venta/${id}/${id}`, { cantidad: 20, subtotal: 500 }, 400);
    assert.equal(await stock(), 7);
    await request('DELETE', `/detalle_venta/${id}/${id}`, undefined, 204);
    assert.equal(await stock(), 10);
    await request('POST', '/detalle_venta', detail(0, 2), 201);
  });
  await t.test('pagos parciales, sobrepago, correcciones y protecciones', async () => {
    const pay = { id_pago: id, id_venta: id, id_metodo_pago: id, monto: 20 };
    await request('POST', '/pago', pay, 201);
    assert.equal((await request('GET', `/venta/${id}`)).estado, 'REGISTRADA');
    await request('PUT', `/detalle_venta/${id}/${id}`, { cantidad: 3, subtotal: 75 }, 409);
    await request('POST', '/pago', { ...pay, id_pago: id + 1, monto: 35 }, 201);
    assert.equal((await request('GET', `/venta/${id}`)).estado, 'PAGADA');
    await request('PUT', `/pago/${id + 1}`, { monto: 5 });
    assert.equal((await request('GET', `/venta/${id}`)).estado, 'REGISTRADA');
    await request('DELETE', `/pago/${id + 1}`, undefined, 204);
    await request('DELETE', `/pago/${id}`, undefined, 204);
    await request('PUT', `/venta/${id}`, { id_estado_venta: 2 }, 409);
    await request('POST', '/venta', sale(1), 201);
    await request('POST', '/pago', { ...pay, id_pago: id + 2, id_venta: id + 1 }, 409);
  });
  await t.test('lotes: suma de stock, rollback total y pagos de varias filas', async () => {
    await request('POST', '/detalle_venta/lote', [detail(1, 1), detail(1, 11, id + 1)], 400);
    assert.equal(await stock(), 8);
    assert.equal(await stock(id + 1), 10);
    await request('GET', `/detalle_venta/${id + 1}/${id}`, undefined, 404);
    await request('POST', '/detalle_venta/lote', [detail(1, 2), detail(1, 1, id + 1)], 201);
    assert.equal(await stock(), 6);
    assert.equal(await stock(id + 1), 9);
    await request('POST', '/pago/lote', [
      { id_pago: id + 3, id_venta: id + 1, id_metodo_pago: id, monto: 25 },
      { id_pago: id + 4, id_venta: id + 1, id_metodo_pago: id, monto: 50 },
    ], 201);
    assert.equal((await request('GET', `/venta/${id + 1}`)).estado, 'PAGADA');
  });
  await t.test('concurrencia: dos solicitudes compiten por las ultimas unidades', async () => {
    await request('POST', '/venta', sale(2), 201);
    await request('POST', '/venta', sale(3), 201);
    const outcomes = await Promise.all([2, 3].map(async n => {
      const res = await fetch(base + '/detalle_venta', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(detail(n, 6)) });
      const body = await res.json();
      proof.push({ scenario: 'concurrencia', status: res.status, response: body });
      return res.status;
    }));
    assert.deepEqual(outcomes.sort(), [201, 400]);
    assert.equal(await stock(), 0);
  });
  await t.test('anulacion restaura una vez y reportes excluyen ventas anuladas', async () => {
    await request('PUT', `/venta/${id}`, { id_estado_venta: 3 });
    assert.equal(await stock(), 2);
    await request('DELETE', `/catalogo_producto/${id}/${id}`, undefined, 409);
    await request('PUT', `/venta/${id}`, { id_estado_venta: 3 }, 409);
    assert.equal(await stock(), 2);
    await request('POST', '/pago', { id_pago: id + 8, id_venta: id, id_metodo_pago: id, monto: 1 }, 409);
    await request('PUT', `/detalle_venta/${id}/${id}`, { cantidad: 1, subtotal: 25 }, 409);
    const locations = await request('GET', '/reportes/ventas-ubicacion');
    const location = locations.data.find((r: any) => r.id_tienda === id);
    assert.equal(Number(location.cantidad_ventas), 3);
    assert.equal(Number(location.total_facturado), 225);
    const top = await request('GET', '/reportes/top-productos');
    const product = top.data.find((r: any) => r.codigo_producto === id);
    assert.equal(Number(product.unidades_vendidas), 8);
    assert.equal(Number(product.monto_total), 200);
    const pending = await request('GET', '/reportes/saldos-pendientes');
    assert.equal(pending.data.some((r: any) => r.id_venta === id || r.id_venta === id + 1), false);
  });
  await t.test('las tres vistas coinciden con una referencia calculada desde la API', async () => {
    const all = async (table: string) => {
      const rows: any[] = [];
      for (let offset = 0; ; offset += 500) {
        const page = await request('GET', `/${table}?limit=500&offset=${offset}`);
        rows.push(...page.data);
        if (rows.length >= page.total) return rows;
      }
    };
    const [ventas, detalles, pagos] = await Promise.all(['venta', 'detalle_venta', 'pago'].map(all));
    const totals = new Map<number, number>();
    const paid = new Map<number, number>();
    for (const d of detalles) totals.set(d.id_venta, (totals.get(d.id_venta) ?? 0) + Math.round(d.subtotal * 100));
    for (const p of pagos) paid.set(p.id_venta, (paid.get(p.id_venta) ?? 0) + Math.round(p.monto * 100));
    const locations = new Map<number, { cantidad: number; total: number }>();
    const active = new Set<number>();
    for (const v of ventas) {
      if (v.estado === 'ANULADA') continue;
      active.add(v.id_venta);
      const row = locations.get(v.id_tienda) ?? { cantidad: 0, total: 0 };
      row.cantidad++; row.total += totals.get(v.id_venta) ?? 0;
      locations.set(v.id_tienda, row);
    }
    const products = new Map<number, { unidades: number; total: number }>();
    for (const d of detalles) if (active.has(d.id_venta)) {
      const row = products.get(d.id_producto) ?? { unidades: 0, total: 0 };
      row.unidades += d.cantidad; row.total += Math.round(d.subtotal * 100);
      products.set(d.id_producto, row);
    }
    const locationReport = (await request('GET', '/reportes/ventas-ubicacion')).data;
    assert.equal(locationReport.length, locations.size);
    for (const r of locationReport) assert.deepEqual({ cantidad: Number(r.cantidad_ventas), total: Math.round(r.total_facturado * 100) }, locations.get(r.id_tienda));
    const productReport = (await request('GET', '/reportes/top-productos')).data;
    assert.equal(productReport.length, products.size);
    for (const r of productReport) assert.deepEqual({ unidades: Number(r.unidades_vendidas), total: Math.round(r.monto_total * 100) }, products.get(r.codigo_producto));
    const pending = (await request('GET', '/reportes/saldos-pendientes')).data;
    assert.equal(pending.length, ventas.filter(v => v.estado === 'REGISTRADA').length);
    for (const r of pending) {
      assert.equal(Math.round(r.total_venta * 100), totals.get(r.id_venta) ?? 0);
      assert.equal(Math.round(r.total_pagado * 100), paid.get(r.id_venta) ?? 0);
      assert.equal(Math.round(r.saldo_pendiente * 100), (totals.get(r.id_venta) ?? 0) - (paid.get(r.id_venta) ?? 0));
    }
  });
  await writeFile('docs/evidencias/integracion.json', JSON.stringify({ fecha: new Date().toISOString(), fixtureId: id, escenarios: proof }, null, 2));
});
