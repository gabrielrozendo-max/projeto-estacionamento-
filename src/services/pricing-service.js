const millisecondsPerHour = 60 * 60 * 1000;

export class PricingError extends Error {
  constructor(code, message) {
    super(message);
    this.name = 'PricingError';
    this.code = code;
  }
}

export function calculateParkingFee(entryAt, exitAt, hourlyPriceCents) {
  const entryTime = Date.parse(entryAt);
  const exitTime = Date.parse(exitAt);

  if (!Number.isFinite(entryTime) || !Number.isFinite(exitTime)) {
    throw new PricingError(
      'INVALID_TIMESTAMP',
      'Parking timestamps must be valid date-time values.',
    );
  }

  if (exitTime < entryTime) {
    throw new PricingError(
      'EXIT_BEFORE_ENTRY',
      'Exit time cannot be earlier than entry time.',
    );
  }

  if (!Number.isSafeInteger(hourlyPriceCents) || hourlyPriceCents < 0) {
    throw new PricingError(
      'INVALID_HOURLY_PRICE',
      'Hourly price must be a non-negative integer in cents.',
    );
  }

  const billableHours = Math.ceil((exitTime - entryTime) / millisecondsPerHour);
  const totalAmountCents = billableHours * hourlyPriceCents;

  if (!Number.isSafeInteger(totalAmountCents)) {
    throw new PricingError(
      'FEE_OUT_OF_RANGE',
      'Calculated parking fee exceeds the supported amount.',
    );
  }

  return totalAmountCents;
}
