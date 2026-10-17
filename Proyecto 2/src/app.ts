import express from 'express';
import { database } from './config/database';
import { errorHandler } from './middleware/errors';
import { entityRoutes } from './routes';
import { adminRouter } from './routes/admin';
import { reportsRouter } from './routes/reportes';

export const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10mb' }));
app.get('/api/health', async (_req, res) => {
  await database.query('SELECT 1 AS conectado');
  res.json({ estado: 'ok', database: 'SQL Server 2022' });
});
app.use('/api/admin', adminRouter);
app.use('/api/reportes', reportsRouter);
for (const [name, router] of Object.entries(entityRoutes)) app.use('/api/' + name, router);
app.use((_req, res) => { res.status(404).json({ error: 'Ruta no encontrada' }); });
app.use(errorHandler);
