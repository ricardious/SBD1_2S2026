import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tables } from '../src/entities';
import { bodySchema, databaseValues, keysFromParams } from '../src/services/validation';

const spec = (name: string) => tables.find(t => t.table === name)!;
test('rechaza campos desconocidos y claves en PUT', () => {
  assert.equal(bodySchema(spec('pais')).safeParse({ id_pais: 1, nombre: 'GT', sql: 'DROP' }).success, false);
  assert.equal(bodySchema(spec('pais'), true).safeParse({ id_pais: 2 }).success, false);
  assert.equal(bodySchema(spec('pais'), true).safeParse({}).success, false);
});
test('preserva Unicode y correo nulo; valida fechas reales y decimales', () => {
  assert.equal(bodySchema(spec('persona')).safeParse({ id_persona: 1, nombres: 'José', apellidos: 'Pérez', telefono: '123', correo: null, direccion: 'Centro', id_municipio: 1 }).success, true);
  const pago = { id_pago: 1, id_venta: 1, id_metodo_pago: 1, monto: 1.001 };
  assert.equal(bodySchema(spec('pago')).safeParse(pago).success, false);
  assert.equal(bodySchema(spec('pago')).safeParse({ ...pago, monto: 1.01 }).success, true);
  const empleado = { id_empleado: 1, fecha_contratacion: '2026-02-30', id_tienda: 1, id_cargo: 1, id_persona: 1 };
  assert.equal(bodySchema(spec('empleado')).safeParse(empleado).success, false);
  assert.equal(bodySchema(spec('empleado')).safeParse({ ...empleado, fecha_contratacion: '2024-02-29' }).success, true);
});
test('claves compuestas son enteros positivos y fechas se envian en UTC', () => {
  assert.deepEqual(keysFromParams(spec('catalogo_producto'), { id_tienda: '1', id_producto: '2' }), { id_tienda: 1, id_producto: 2 });
  assert.throws(() => keysFromParams(spec('pais'), { id_pais: '1 OR 1=1' }));
  assert.throws(() => keysFromParams(spec('pais'), { id_pais: '2147483648' }));
  assert.equal((databaseValues(spec('venta'), { fecha_venta: '2026-10-16T14:30:00' }).fecha_venta as Date).toISOString(), '2026-10-16T14:30:00.000Z');
});
