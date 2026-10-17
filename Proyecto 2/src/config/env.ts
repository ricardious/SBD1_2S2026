import 'dotenv/config';
import { z } from 'zod';

const boolean = z.enum(['true', 'false']).transform(v => v === 'true');
export const env = z.object({
  DB_HOST: z.string().default('127.0.0.1'),
  DB_PORT: z.coerce.number().int().min(1).max(65535).default(1433),
  DB_NAME: z.string().default('ComercialLaEstrella'),
  DB_USER: z.string().default('estrella_api'),
  DB_PASSWORD: z.string().min(16),
  IMPORT_DB_USER: z.string().default('estrella_import'),
  IMPORT_DB_PASSWORD: z.string().min(16),
  IMPORT_KEY: z.string().min(32),
  IMPORT_ENABLED: boolean.default(false),
  HOST: z.string().default('127.0.0.1'),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
}).parse(process.env);
