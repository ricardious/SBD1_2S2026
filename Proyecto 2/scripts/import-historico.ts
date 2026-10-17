import 'dotenv/config';
import { readFile } from 'node:fs/promises';

async function main() {
  const base = process.env.API_URL ?? `http://127.0.0.1:${process.env.PORT ?? 3000}/api`;
  const response = await fetch(`${base}/admin/importacion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Import-Key': process.env.IMPORT_KEY ?? '' },
    body: await readFile('data/historico.json', 'utf8'),
    signal: AbortSignal.timeout(180000),
  });
  const result = await response.json();
  console.log(JSON.stringify(result, null, 2));
  if (!response.ok) process.exitCode = 1;
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
