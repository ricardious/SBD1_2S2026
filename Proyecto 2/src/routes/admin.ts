import { timingSafeEqual } from 'node:crypto';
import { Router } from 'express';
import { env } from '../config/env';
import { HttpError } from '../middleware/errors';
import { importHistorico, importStatus } from '../services/historico';

export const adminRouter = Router();
adminRouter.get('/importacion', async (_req, res) => { res.json({ ...await importStatus(), habilitada: env.IMPORT_ENABLED }); });
adminRouter.post('/importacion', (req, _res, next) => {
  if (!env.IMPORT_ENABLED) throw new HttpError(404, 'Ruta no disponible');
  const supplied = Buffer.from(req.get('X-Import-Key') ?? '');
  const expected = Buffer.from(env.IMPORT_KEY);
  if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) throw new HttpError(401, 'Clave de importacion invalida');
  next();
}, async (req, res) => { res.status(201).json(await importHistorico(req.body)); });
