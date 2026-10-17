import { tables } from '../entities';
import { crudRouter } from './crud';

export default crudRouter(tables.find(t => t.table === 'catalogo_producto')!);
