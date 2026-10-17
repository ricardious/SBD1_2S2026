import { ErrorRequestHandler } from 'express';
import { ZodError } from 'zod';

export class HttpError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

function sqlNumber(error: any): number | undefined {
  return error?.number ?? error?.driverError?.number ?? error?.originalError?.info?.number;
}
export const errorHandler: ErrorRequestHandler = (error, _req, res, _next) => {
  if (error instanceof ZodError) {
    res.status(400).json({ error: 'Datos invalidos', detalles: error.issues.map(i => ({ campo: i.path.join('.'), mensaje: i.message })) });
    return;
  }
  if (error instanceof HttpError) { res.status(error.status).json({ error: error.message }); return; }
  const candidates = [error, error?.driverError, error?.originalError, ...(error?.driverError?.precedingErrors ?? []), ...(error?.precedingErrors ?? [])];
  const business = candidates.find(e => [51001, 51002].includes(sqlNumber(e) ?? 0));
  if (business) {
    const number = sqlNumber(business);
    res.status(number === 51001 ? 400 : 409).json({ error: number === 51001 ? 'Stock insuficiente' : business.message.replace(/^Error: /, '') });
    return;
  }
  const number = candidates.map(sqlNumber).find(n => n !== undefined);
  if (number && [2601, 2627, 547, 1205, 1222].includes(number)) {
    const message = [2601, 2627].includes(number) ? 'Registro duplicado' : number === 547 ? 'Conflicto de integridad o registros asociados' : 'Conflicto concurrente; vuelva a intentar';
    res.status(409).json({ error: message }); return;
  }
  if (error?.type === 'entity.parse.failed') { res.status(400).json({ error: 'JSON invalido' }); return; }
  if (error?.type === 'entity.too.large') { res.status(413).json({ error: 'Cuerpo demasiado grande' }); return; }
  console.error('Error interno:', error instanceof Error ? error.message : 'desconocido');
  res.status(500).json({ error: 'Error interno del servidor' });
};
