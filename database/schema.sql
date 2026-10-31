 CREATE TABLE IF NOT EXISTS tariffs (
  vehicle_type TEXT PRIMARY KEY,
  hourly_price_cents INTEGER NOT NULL CHECK (hourly_price_cents >= 0)
) STRICT;

CREATE TABLE IF NOT EXISTS vehicles (
  plate TEXT PRIMARY KEY CHECK (length(trim(plate)) > 0),
  vehicle_type TEXT NOT NULL REFERENCES tariffs (vehicle_type)
) STRICT;

CREATE TABLE IF NOT EXISTS parking_records (
  id INTEGER PRIMARY KEY,
  plate TEXT NOT NULL REFERENCES vehicles (plate),
  entry_at TEXT NOT NULL,
  exit_at TEXT,
  status TEXT NOT NULL CHECK (
    status IN ('Estacionado', 'Aguardando Pagamento', 'Concluído')
  ),
  total_amount_cents INTEGER CHECK (total_amount_cents >= 0),
  CHECK (
    (status = 'Estacionado' AND exit_at IS NULL AND total_amount_cents IS NULL)
    OR (
      status IN ('Aguardando Pagamento', 'Concluído')
      AND exit_at IS NOT NULL
      AND total_amount_cents IS NOT NULL
    )
  )
) STRICT;

CREATE TABLE IF NOT EXISTS parking_capacity (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  max_capacity INTEGER NOT NULL CHECK (max_capacity > 0),
  occupied_spaces INTEGER NOT NULL DEFAULT 0
    CHECK (occupied_spaces >= 0 AND occupied_spaces <= max_capacity)
) STRICT;
