import { Router } from 'express';
import { TableSpec } from '../entities';
import { crudController } from '../controllers/crud';

export function crudRouter(spec: TableSpec) {
  const router = Router();
  const controller = crudController(spec);
  const path = '/' + spec.keys.map(k => ':' + k).join('/');
  router.get('/', controller.list);
  router.post('/', controller.create);
  if (['detalle_venta', 'pago'].includes(spec.table)) router.post('/lote', controller.batch);
  router.get(path, controller.get);
  router.put(path, controller.update);
  router.delete(path, controller.delete);
  return router;
}
