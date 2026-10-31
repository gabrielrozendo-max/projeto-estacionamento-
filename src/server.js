import { createApp } from './app.js';
import { openDatabase } from './config/database.js';

const port = Number(process.env.PORT ?? 3000);

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT tem de ser um número entre 1 e 65535.');
}

const database = await openDatabase();
const server = createApp(database).listen(port, () => {
  console.log(`API de estacionamento disponível na porta ${port}.`);
});

server.on('error', async (error) => {
  console.error('Não foi possível iniciar o servidor:', error);
  await closeDatabase(database);
  process.exitCode = 1;
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.once(signal, () => {
    server.close(async (error) => {
      if (error) {
        console.error('Erro ao encerrar o servidor:', error);
        process.exitCode = 1;
      }

      await closeDatabase(database);
    });
  });
}

function closeDatabase(connection) {
  return new Promise((resolve) => {
    connection.close((error) => {
      if (error) {
        console.error('Erro ao fechar a base de dados:', error);
        process.exitCode = 1;
      }

      resolve();
    });
  });
}
