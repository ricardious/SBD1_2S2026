import { RequestHandler } from 'express';
import { z } from 'zod';
import { database } from '../config/database';
import { TableSpec } from '../entities';
import { HttpError } from '../middleware/errors';
import { bodySchema, databaseValues, keysFromParams } from '../services/validation';

export function crudController(spec: TableSpec): Record<string, RequestHandler> {
  const repository = () => database.getRepository(spec.table);
  const getOne = async (keys: Record<string, number>) => {
    if (spec.table === 'venta') {
      const rows = await database.query('SELECT * FROM dbo.Vista_Consulta_Ventas WHERE id_venta=@0', [keys.id_venta]);
      return rows[0] ?? null;
    }
    return repository().findOneBy(keys);
  };
  return {
    batch: async (req, res) => {
      const rows = z.array(bodySchema(spec)).min(1).max(100).parse(req.body);
      await repository().insert(rows.map(row => databaseValues(spec, row)));
      res.status(201).json({ insertados: rows.length });
    },
    list: async (req, res) => {
      const query = z.strictObject({
        limit: z.coerce.number().int().min(1).max(500).default(100),
        offset: z.coerce.number().int().min(0).max(2147483000).default(0),
      }).parse(req.query);
      const data = spec.table === 'venta'
        ? await database.query('SELECT * FROM dbo.Vista_Consulta_Ventas ORDER BY id_venta OFFSET @0 ROWS FETCH NEXT @1 ROWS ONLY', [query.offset, query.limit])
        : await repository().find({ take: query.limit, skip: query.offset, order: Object.fromEntries(spec.keys.map(k => [k, 'ASC'])) });
      res.json({ data, total: await repository().count(), ...query });
    },
    get: async (req, res) => {
      const row = await getOne(keysFromParams(spec, req.params as Record<string, string>));
      if (!row) throw new HttpError(404, 'Registro no encontrado');
      res.json(row);
    },
    create: async (req, res) => {
      const parsed = bodySchema(spec).parse(req.body);
      await repository().insert(databaseValues(spec, parsed));
      const keys = Object.fromEntries(spec.keys.map(k => [k, parsed[k] as number]));
      res.status(201).json(await getOne(keys));
    },
    update: async (req, res) => {
      const keys = keysFromParams(spec, req.params as Record<string, string>);
      const parsed = bodySchema(spec, true).parse(req.body);
      // Claves de asociaciones financieras no se trasladan a otra venta/producto.
      if (spec.table === 'pago' && 'id_venta' in parsed) throw new HttpError(400, 'id_venta no se modifica en un pago');
      const result = await repository().update(keys, databaseValues(spec, parsed));
      if (!result.affected) throw new HttpError(404, 'Registro no encontrado');
      res.json(await getOne(keys));
    },
    delete: async (req, res) => {
      const result = await repository().delete(keysFromParams(spec, req.params as Record<string, string>));
      if (!result.affected) throw new HttpError(404, 'Registro no encontrado');
      res.sendStatus(204);
    },
  };
}
