import { AppError } from '../errors/app-error.js';
import {
  calculateParkingFee,
  PricingError,
} from '../services/pricing-service.js';

const transactionQueues = new WeakMap();

export async function registerVehicleEntry(
  database,
  { plate, vehicleType, entryAt },
) {
  return withTransaction(database, async () => {
    const capacity = await get(
      database,
      'SELECT max_capacity AS maxCapacity, occupied_spaces AS occupiedSpaces FROM parking_capacity WHERE id = 1',
    );

    if (!capacity) {
      throw new AppError(
        503,
        'PARKING_NOT_CONFIGURED',
        'A capacidade do parque ainda não foi configurada.',
      );
    }

    if (capacity.occupiedSpaces >= capacity.maxCapacity) {
      throw new AppError(409, 'PARKING_FULL', 'O parque está lotado.');
    }

    const tariff = await get(
      database,
      'SELECT vehicle_type AS vehicleType FROM tariffs WHERE vehicle_type = ?',
      [vehicleType],
    );

    if (!tariff) {
      throw new AppError(
        400,
        'UNKNOWN_VEHICLE_TYPE',
        'Não existe uma tarifa configurada para este tipo de veículo.',
      );
    }

    const vehicle = await get(
      database,
      'SELECT vehicle_type AS vehicleType FROM vehicles WHERE plate = ?',
      [plate],
    );

    if (vehicle && vehicle.vehicleType !== vehicleType) {
      throw new AppError(
        409,
        'VEHICLE_TYPE_CONFLICT',
        'A matrícula já está associada a outro tipo de veículo.',
      );
    }

    if (!vehicle) {
      await run(
        database,
        'INSERT INTO vehicles (plate, vehicle_type) VALUES (?, ?)',
        [plate, vehicleType],
      );
    }

    const activeRecord = await get(
      database,
      "SELECT id FROM parking_records WHERE plate = ? AND status = 'Estacionado'",
      [plate],
    );

    if (activeRecord) {
      throw new AppError(
        409,
        'VEHICLE_ALREADY_PARKED',
        'Já existe um registo de estacionamento ativo para esta matrícula.',
      );
    }

    const result = await run(
      database,
      "INSERT INTO parking_records (plate, entry_at, status) VALUES (?, ?, 'Estacionado')",
      [plate, entryAt],
    );

    const occupancy = await run(
      database,
      'UPDATE parking_capacity SET occupied_spaces = occupied_spaces + 1 WHERE id = 1 AND occupied_spaces < max_capacity',
    );

    if (occupancy.changes !== 1) {
      throw new AppError(
        409,
        'PARKING_FULL',
        'O parque está lotado.',
      );
    }

    return {
      id: result.lastID,
      plate,
      vehicleType,
      entryAt,
      status: 'Estacionado',
      occupiedSpaces: capacity.occupiedSpaces + 1,
      maxCapacity: capacity.maxCapacity,
    };
  });
}

export async function registerVehicleExit(database, { plate, exitAt }) {
  return withTransaction(database, async () => {
    const record = await get(
      database,
      `SELECT
         parking_records.id AS id,
         parking_records.plate AS plate,
         parking_records.entry_at AS entryAt,
         vehicles.vehicle_type AS vehicleType,
         tariffs.hourly_price_cents AS hourlyPriceCents
       FROM parking_records
       JOIN vehicles ON vehicles.plate = parking_records.plate
       JOIN tariffs ON tariffs.vehicle_type = vehicles.vehicle_type
       WHERE parking_records.plate = ?
         AND parking_records.status = 'Estacionado'`,
      [plate],
    );

    if (!record) {
      throw new AppError(
        404,
        'ACTIVE_PARKING_RECORD_NOT_FOUND',
        'Não foi encontrado um registo de estacionamento ativo para esta matrícula.',
      );
    }

    const capacity = await get(
      database,
      'SELECT occupied_spaces AS occupiedSpaces FROM parking_capacity WHERE id = 1',
    );

    if (!capacity || capacity.occupiedSpaces < 1) {
      throw new AppError(
        500,
        'OCCUPANCY_INCONSISTENT',
        'A lotação do parque está inconsistente com os registos de estacionamento.',
      );
    }

    let totalAmountCents;
    try {
      totalAmountCents = calculateParkingFee(
        record.entryAt,
        exitAt,
        record.hourlyPriceCents,
      );
    } catch (error) {
      if (!(error instanceof PricingError)) {
        throw error;
      }

      const status = error.code === 'EXIT_BEFORE_ENTRY' ? 400 : 500;
      throw new AppError(status, error.code, error.message);
    }

    const update = await run(
      database,
      `UPDATE parking_records
       SET exit_at = ?, total_amount_cents = ?, status = 'Aguardando Pagamento'
       WHERE id = ? AND status = 'Estacionado'`,
      [exitAt, totalAmountCents, record.id],
    );

    if (update.changes !== 1) {
      throw new AppError(
        409,
        'PARKING_RECORD_CHANGED',
        'O registo de estacionamento foi alterado. Tente novamente.',
      );
    }

    const occupancy = await run(
      database,
      'UPDATE parking_capacity SET occupied_spaces = occupied_spaces - 1 WHERE id = 1 AND occupied_spaces > 0',
    );

    if (occupancy.changes !== 1) {
      throw new AppError(
        500,
        'OCCUPANCY_INCONSISTENT',
        'A lotação do parque está inconsistente com os registos de estacionamento.',
      );
    }

    return {
      id: record.id,
      plate: record.plate,
      vehicleType: record.vehicleType,
      entryAt: record.entryAt,
      exitAt,
      status: 'Aguardando Pagamento',
      totalAmountCents,
      occupiedSpaces: capacity.occupiedSpaces - 1,
    };
  });
}

async function withTransaction(database, operation) {
  const previous = transactionQueues.get(database) ?? Promise.resolve();
  const transaction = previous.then(async () => {
    await run(database, 'BEGIN IMMEDIATE');

    try {
      const result = await operation();
      await run(database, 'COMMIT');
      return result;
    } catch (error) {
      try {
        await run(database, 'ROLLBACK');
      } catch (rollbackError) {
        throw new AggregateError(
          [error, rollbackError],
          'The database operation failed and its transaction could not be rolled back.',
        );
      }

      throw error;
    }
  });

  transactionQueues.set(database, transaction.catch(() => {}));
  return transaction;
}

function run(database, sql, parameters = []) {
  return new Promise((resolve, reject) => {
    database.run(sql, parameters, function (error) {
      if (error) {
        reject(error);
        return;
      }

      resolve({ changes: this.changes, lastID: this.lastID });
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
