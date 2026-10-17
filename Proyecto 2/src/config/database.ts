import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { entities } from '../entities';
import { env } from './env';

function connection(username: string, password: string, max: number): DataSource {
  return new DataSource({
    type: 'mssql', host: env.DB_HOST, port: env.DB_PORT, database: env.DB_NAME,
    username, password, entities, synchronize: false, migrationsRun: false,
    logging: false, pool: { max, min: 0 }, requestTimeout: 120000,
    options: {
      encrypt: true, trustServerCertificate: true, useUTC: true,
      // OUTPUT sin INTO no es compatible con tablas que tienen triggers.
      disableOutputReturning: true,
    },
  });
}
export const database = connection(env.DB_USER, env.DB_PASSWORD, 5);
// Nunca se usa esta conexion en rutas CRUD. Se abre solo para una importacion.
export const importDatabase = connection(env.IMPORT_DB_USER, env.IMPORT_DB_PASSWORD, 1);
