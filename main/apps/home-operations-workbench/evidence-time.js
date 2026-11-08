// Strict saved evidence time: explicit offset, real calendar, no Date rollover.
export function parseObservation(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,6})?(?:Z|[+-](?:(?:0\d|1[0-3]):[0-5]\d|14:00))$/.test(value)) return null;
  const day = new Date(`${value.slice(0, 10)}T00:00:00Z`);
  const date = new Date(value);
  return Number.isFinite(day.valueOf()) && day.toISOString().slice(0, 10) === value.slice(0, 10) && Number.isFinite(date.valueOf()) ? date : null;
}
