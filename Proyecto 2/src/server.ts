import { app } from './app';
import { database, importDatabase } from './config/database';
import { env } from './config/env';

async function main() {
  await database.initialize();
  const server = app.listen(env.PORT, env.HOST, () => console.log(`API disponible en http://${env.HOST}:${env.PORT}/api`));
  const close = () => {
    server.close(async () => {
      if (importDatabase.isInitialized) await importDatabase.destroy();
      await database.destroy();
      process.exit(0);
    });
  };
  process.on('SIGTERM', close);
  process.on('SIGINT', close);
}
main().catch(error => { console.error('No se pudo iniciar la API:', error.message); process.exitCode = 1; });
