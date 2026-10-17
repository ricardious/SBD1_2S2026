import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { database, importDatabase } from '../config/database';
import { tables } from '../entities';
import { HttpError } from '../middleware/errors';
import { bodySchema, databaseValues } from './validation';

export function canonical(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.entries(value)
    .sort(([a], [b]) => a.localeCompare(b, 'en'))
    .map(([key, v]) => JSON.stringify(key) + ':' + canonical(v)).join(',') + '}';
  return JSON.stringify(value);
}
export const digest = (value: unknown) => createHash('sha256').update(canonical(value)).digest('hex');
let importing = false;

export async function importHistorico(payload: unknown) {
  if (importing) throw new HttpError(409, 'Ya existe una importacion en curso');
  // Reservar antes del primer await: dos lecturas de archivo no deben abrir el mismo pool.
  importing = true;
  try {
    const original = JSON.parse(await readFile(resolve('data/historico.json'), 'utf8'));
    // La excepcion historica solo admite el archivo original, nunca operaciones nuevas.
    if (digest(payload) !== digest(original)) throw new HttpError(400, 'El archivo no coincide con el historico original');
    const input = payload as Record<string, Record<string, unknown>[]>;
    for (const spec of tables) for (const row of input[spec.table]) bodySchema(spec).parse(row);
    await importDatabase.initialize();
    const runner = importDatabase.createQueryRunner();
    await runner.connect();
    try {
      await runner.startTransaction('SERIALIZABLE');
      await runner.query(`DECLARE @result INT;
        EXEC @result = sp_getapplock @Resource=N'importacion_historica', @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=0;
        IF @result < 0 THROW 51002, N'Importacion en curso',1;`);
      const done = await runner.query('SELECT id FROM dbo.importacion_historica WITH (UPDLOCK,HOLDLOCK)');
      if (done.length) throw new HttpError(409, 'El historico ya fue importado');
      for (const spec of tables) {
        if (await runner.manager.getRepository(spec.table).count()) throw new HttpError(409, 'La importacion requiere las 19 tablas vacias');
      }
      await runner.query("EXEC sys.sp_set_session_context @key=N'importacion_historica', @value=1");
      for (const spec of tables) {
        const repository = runner.manager.getRepository(spec.table);
        for (let start = 0; start < input[spec.table].length; start += 50) {
          await repository.insert(input[spec.table].slice(start, start + 50).map(row => databaseValues(spec, row)));
        }
      }
      const counts: Record<string, number> = {};
      // Conciliar todos los valores, no solo el numero de filas.
      for (const spec of tables) {
        const rows = await runner.manager.getRepository(spec.table).find({ order: Object.fromEntries(spec.keys.map(k => [k, 'ASC'])) });
        const normalized = rows.map(row => Object.fromEntries(Object.entries(row).map(([k, v]) => [k, v instanceof Date ? v.toISOString().slice(0, 19) : v])));
        const sortedOriginal = [...input[spec.table]].sort((a, b) => {
          for (const key of spec.keys) { const diff = Number(a[key]) - Number(b[key]); if (diff) return diff; }
          return 0;
        });
        if (digest(normalized) !== digest(sortedOriginal)) throw new Error(`Fallo de conciliacion en ${spec.table}`);
        counts[spec.table] = rows.length;
      }
      const total = Object.values(counts).reduce((a, b) => a + b, 0);
      const sha256 = digest(original);
      await runner.query('INSERT dbo.importacion_historica(id,filas,sha256) VALUES(1,@0,@1)', [total, sha256]);
      await runner.query("EXEC sys.sp_set_session_context @key=N'importacion_historica', @value=NULL");
      await runner.commitTransaction();
      return { mensaje: 'Historico importado y conciliado', counts, total, sha256 };
    } catch (error) {
      if (runner.isTransactionActive) await runner.rollbackTransaction();
      throw error;
    } finally {
      // SESSION_CONTEXT no se limpia automaticamente al devolver una conexion al pool.
      try { await runner.query("EXEC sys.sp_set_session_context @key=N'importacion_historica', @value=NULL"); }
      finally { await runner.release(); }
    }
  } finally {
    if (importDatabase.isInitialized) await importDatabase.destroy();
    importing = false;
  }
}

export async function importStatus() {
  const rows = await database.query('SELECT fecha,filas,sha256 FROM dbo.importacion_historica WHERE id=1');
  return { importado: rows.length > 0, detalle: rows[0] ?? null };
}
