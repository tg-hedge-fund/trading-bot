-- Fixes creation_ts DEFAULT: previously `now() AT TIME ZONE 'UTC'` converted the
-- timestamptz into a naive UTC timestamp, which then got re-interpreted using the
-- session's timezone on insert into the timestamptz column, corrupting the stored
-- instant. `now()` already stores the correct instant for timestamptz columns.
-- Run once per environment (dev/prod).

ALTER TABLE "primary".instrument_eq ALTER COLUMN creation_ts SET DEFAULT now();
ALTER TABLE "primary".instrument_idx ALTER COLUMN creation_ts SET DEFAULT now();
ALTER TABLE "primary".portfolio ALTER COLUMN creation_ts SET DEFAULT now();
