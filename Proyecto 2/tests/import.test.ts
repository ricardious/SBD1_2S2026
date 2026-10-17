import { test } from 'node:test';
import assert from 'node:assert/strict';
import { importHistorico } from '../src/services/historico';
import { HttpError } from '../src/middleware/errors';

test('la exclusion de importaciones se adquiere antes de leer el archivo y se libera al fallar', async () => {
  const results = await Promise.allSettled([importHistorico({}), importHistorico({})]);
  const codes = results.map(result => {
    assert.equal(result.status, 'rejected');
    if (result.status !== 'rejected') throw new Error('Se acepto un archivo invalido');
    assert.ok(result.reason instanceof HttpError);
    return result.reason.status;
  });
  assert.deepEqual(codes, [400, 409]);
  await assert.rejects(importHistorico({}), (error: unknown) => error instanceof HttpError && error.status === 400);
});
