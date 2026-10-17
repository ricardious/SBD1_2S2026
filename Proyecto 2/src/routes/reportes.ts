import { Router } from 'express';
import { database } from '../config/database';

export const reportsRouter = Router();
// Lista cerrada: nunca interpolar un nombre de vista recibido del usuario.
for (const [path, view, order] of [
  ['ventas-ubicacion', 'Vista_Ventas_Ubicacion', 'id_tienda'],
  ['top-productos', 'Vista_Top_Productos', 'unidades_vendidas DESC, codigo_producto'],
  ['saldos-pendientes', 'Vista_Saldos_Pendientes', 'id_venta'],
]) {
  reportsRouter.get('/' + path, async (_req, res) => {
    res.json({ data: await database.query(`SELECT * FROM dbo.${view} ORDER BY ${order}`) });
  });
}
