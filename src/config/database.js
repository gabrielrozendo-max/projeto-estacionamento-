import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import sqlite3 from 'sqlite3';

const databasePath = fileURLToPath(
  new URL('../../database/parking.sqlite', import.meta.url),
);
const schemaPath = fileURLToPath(
  new URL('../../database/schema.sql', import.meta.url),
);

export function openDatabase() {
  return new Promise((resolve, reject) => {
    const database = new sqlite3.Database(
      databasePath,
      sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE,
      (openError) => {
        if (openError) {
          reject(openError);
          return;
        }

        database.configure('busyTimeout', 5000);
        database.run('PRAGMA foreign_keys = ON', (pragmaError) => {
          if (pragmaError) {
            closeAfterInitializationError(database, pragmaError, reject);
            return;
          }

          initializeSchema(database)
            .then(() => resolve(database))
            .catch((schemaError) => {
              closeAfterInitializationError(database, schemaError, reject);
            });
        });
      },
    );
  });
}

async function initializeSchema(database) {
  const schema = await readFile(schemaPath, 'utf8');

  await new Promise((resolve, reject) => {
    database.exec(schema, (error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
}

function closeAfterInitializationError(database, initializationError, reject) {
  database.close((closeError) => {
    if (closeError) {
      reject(
        new AggregateError(
          [initializationError, closeError],
          'Database initialization failed and the connection could not be closed.',
        ),
      );
      return;
    }

    reject(initializationError);
  });
}
