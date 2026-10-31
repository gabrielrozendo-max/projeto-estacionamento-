import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { once } from 'node:events';
import { test } from 'node:test';
import sqlite3 from 'sqlite3';
import { createApp } from '../../src/app.js';
import {
  calculateParkingFee,
  PricingError,
} from '../../src/services/pricing-service.js';

test('calcula tarifas em cêntimos e arredonda frações para cima', () => {
  assert.equal(
    calculateParkingFee(
      '2026-10-30T10:00:00.000Z',
      '2026-10-30T11:00:00.000Z',
      125,
    ),
    125,
  );
  assert.equal(
    calculateParkingFee(
      '2026-10-30T10:00:00.000Z',
      '2026-10-30T11:00:00.001Z',
      125,
    ),
    250,
  );
});

test('rejeita uma saída anterior à entrada', () => {
  assert.throws(
    () => calculateParkingFee(
      '2026-10-30T11:00:00.000Z',
      '2026-10-30T10:00:00.000Z',
      125,
    ),
    (error) => error instanceof PricingError && error.code === 'EXIT_BEFORE_ENTRY',
  );
});

test('regista entrada e saída com pagamento pendente e lotação atualizada', async () => {
  const { database, server, baseUrl } = await createTestServer();

  try {
    const entryResponse = await fetch(`${baseUrl}/api/parking/entries`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plate: ' aa-00-aa ', vehicleType: 'Carro' }),
    });
    const entryBody = await entryResponse.json();

    assert.equal(entryResponse.status, 201);
    assert.equal(entryBody.data.plate, 'AA-00-AA');
    assert.equal(entryBody.data.status, 'Estacionado');
    assert.equal(entryBody.occupancy.occupiedSpaces, 1);
    assert.equal(entryBody.occupancy.maxCapacity, 1);

    const duplicateResponse = await fetch(`${baseUrl}/api/parking/entries`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plate: 'AA-00-AA', vehicleType: 'Carro' }),
    });
    assert.equal(duplicateResponse.status, 409);

    const exitResponse = await fetch(`${baseUrl}/api/parking/exits`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plate: 'AA-00-AA' }),
    });
    const exitBody = await exitResponse.json();

    assert.equal(exitResponse.status, 200);
    assert.equal(exitBody.data.status, 'Aguardando Pagamento');
    assert.equal(exitBody.data.totalAmountCents, 100);
    assert.equal(exitBody.occupancy.occupiedSpaces, 0);

    const record = await get(
      database,
      'SELECT status, total_amount_cents AS totalAmountCents FROM parking_records WHERE id = ?',
      [entryBody.data.id],
    );
    assert.deepEqual(record, {
      status: 'Aguardando Pagamento',
      totalAmountCents: 100,
    });
  } finally {
    await closeTestServer(server, database);
  }
});

test('devolve erros JSON para parque cheio e pedido inválido', async () => {
  const { database, server, baseUrl } = await createTestServer(1);

  try {
    const fullResponse = await fetch(`${baseUrl}/api/parking/entries`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plate: 'BB-11-BB', vehicleType: 'Carro' }),
    });
    assert.equal(fullResponse.status, 409);
    assert.equal((await fullResponse.json()).error.code, 'PARKING_FULL');

    const invalidResponse = await fetch(`${baseUrl}/api/parking/entries`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: '{',
    });
    assert.equal(invalidResponse.status, 400);
    assert.equal((await invalidResponse.json()).error.code, 'INVALID_JSON');
  } finally {
    await closeTestServer(server, database);
  }
});

test('não excede a lotação quando chegam entradas concorrentes', async () => {
  const { database, server, baseUrl } = await createTestServer();

  try {
    const responses = await Promise.all(
      ['CC-22-CC', 'DD-33-DD'].map((plate) => fetch(`${baseUrl}/api/parking/entries`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ plate, vehicleType: 'Carro' }),
      })),
    );

    assert.deepEqual(
      responses.map((response) => response.status).sort(),
      [201, 409],
    );

    const occupancy = await get(
      database,
      'SELECT occupied_spaces AS occupiedSpaces FROM parking_capacity WHERE id = 1',
    );
    const activeRecords = await get(
      database,
      "SELECT count(*) AS count FROM parking_records WHERE status = 'Estacionado'",
    );

    assert.equal(occupancy.occupiedSpaces, 1);
    assert.equal(activeRecords.count, 1);
  } finally {
    await closeTestServer(server, database);
  }
});

async function createTestServer(occupiedSpaces = 0) {
  const database = await new Promise((resolve, reject) => {
    const connection = new sqlite3.Database(':memory:', (error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve(connection);
    });
  });
  const schema = await readFile(new URL('../../database/schema.sql', import.meta.url), 'utf8');

  await run(database, 'PRAGMA foreign_keys = ON');
  await new Promise((resolve, reject) => {
    database.exec(schema, (error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
  await run(
    database,
    'INSERT INTO tariffs (vehicle_type, hourly_price_cents) VALUES (?, ?)',
    ['Carro', 100],
  );
  await run(
    database,
    'INSERT INTO parking_capacity (id, max_capacity, occupied_spaces) VALUES (1, 1, ?)',
    [occupiedSpaces],
  );

  const server = createApp(database).listen(0);
  await once(server, 'listening');
  const address = server.address();

  return {
    database,
    server,
    baseUrl: `http://127.0.0.1:${address.port}`,
  };
}

function run(database, sql, parameters = []) {
  return new Promise((resolve, reject) => {
    database.run(sql, parameters, (error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
}

function get(database, sql, parameters = []) {
  return new Promise((resolve, reject) => {
    database.get(sql, parameters, (error, row) => {
      if (error) {
        reject(error);
        return;
      }

      resolve(row);
    });
  });
}

async function closeTestServer(server, database) {
  await new Promise((resolve, reject) => {
    server.close((error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });

  await new Promise((resolve, reject) => {
    database.close((error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
}
