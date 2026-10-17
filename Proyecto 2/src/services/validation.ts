import { z } from 'zod';
import { TableSpec } from '../entities';

const sqlDate = z.string().regex(/^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$/)
  .refine(v => {
    const d = new Date(v.length === 10 ? `${v}T00:00:00Z` : `${v}Z`);
    return Number.isFinite(d.getTime()) && d.toISOString().slice(0, v.length) === v && d.getUTCFullYear() >= 1;
  }, 'Fecha invalida; use YYYY-MM-DD o YYYY-MM-DDTHH:mm:ss');

export function bodySchema(spec: TableSpec, update = false) {
  const fields: Record<string, z.ZodType> = {};
  for (const [name, field] of Object.entries(spec.fields)) {
    if (update && spec.keys.includes(name)) continue;
    let validator: z.ZodType;
    if (field.type === 'integer') validator = z.number().int().min(name === 'existencia_actual' ? 0 : 1).max(2147483647);
    else if (field.type === 'decimal') validator = z.number().positive().max(9999999999.99)
      .refine(v => Math.abs(v * 100 - Math.round(v * 100)) < 0.0001, 'Se requieren como maximo dos decimales');
    else if (field.type === 'date') validator = sqlDate;
    else validator = z.string().min(1).max(field.length ?? 300).refine(v => v.trim().length > 0, 'No puede estar vacio');
    if (name === 'correo') validator = z.email().max(field.length ?? 150);
    if (field.nullable) validator = validator.nullable();
    fields[name] = validator;
  }
  const schema = z.strictObject(fields);
  return update ? schema.partial().refine(v => Object.keys(v).length > 0, 'Envie al menos un campo modificable') : schema;
}

export function keysFromParams(spec: TableSpec, params: Record<string, string>) {
  return Object.fromEntries(spec.keys.map(key => {
    const value = z.string().regex(/^[1-9]\d*$/).parse(params[key]);
    return [key, z.number().int().max(2147483647).parse(Number(value))];
  }));
}

export function databaseValues(spec: TableSpec, body: Record<string, unknown>) {
  return Object.fromEntries(Object.entries(body).map(([name, value]) => [name,
    spec.fields[name].type === 'date' && typeof value === 'string'
      ? new Date(value.length === 10 ? `${value}T00:00:00Z` : `${value}Z`) : value,
  ]));
}
