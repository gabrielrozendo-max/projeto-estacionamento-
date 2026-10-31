import { AppError } from '../errors/app-error.js';
import {
  registerVehicleEntry,
  registerVehicleExit,
} from '../models/parking-model.js';

export function createParkingController(database) {
  return {
    registerEntry: async (request, response) => {
      const { plate, vehicleType } = validateVehiclePayload(request.body);
      const entryAt = new Date().toISOString();
      const result = await registerVehicleEntry(database, {
        plate,
        vehicleType,
        entryAt,
      });

      response.status(201).json({
        data: {
          id: result.id,
          plate: result.plate,
          vehicleType: result.vehicleType,
          entryAt: result.entryAt,
          status: result.status,
        },
        occupancy: {
          occupiedSpaces: result.occupiedSpaces,
          maxCapacity: result.maxCapacity,
        },
      });
    },

    registerExit: async (request, response) => {
      const { plate } = validateVehiclePayload(request.body);
      const exitAt = new Date().toISOString();
      const result = await registerVehicleExit(database, { plate, exitAt });

      response.status(200).json({
        data: {
          id: result.id,
          plate: result.plate,
          vehicleType: result.vehicleType,
          entryAt: result.entryAt,
          exitAt: result.exitAt,
          status: result.status,
          totalAmountCents: result.totalAmountCents,
        },
        occupancy: {
          occupiedSpaces: result.occupiedSpaces,
        },
      });
    },
  };
}

function validateVehiclePayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new AppError(400, 'INVALID_REQUEST_BODY', 'O corpo do pedido deve ser um objeto JSON.');
  }

  const plate = typeof payload.plate === 'string'
    ? payload.plate.trim().toUpperCase()
    : '';

  if (!plate) {
    throw new AppError(400, 'INVALID_PLATE', 'A matrícula é obrigatória.');
  }

  if (payload.vehicleType !== undefined) {
    if (typeof payload.vehicleType !== 'string' || !payload.vehicleType.trim()) {
      throw new AppError(
        400,
        'INVALID_VEHICLE_TYPE',
        'O tipo de veículo deve ser um texto não vazio.',
      );
    }

    return { plate, vehicleType: payload.vehicleType.trim() };
  }

  return { plate };
}
