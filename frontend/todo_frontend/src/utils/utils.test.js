import { formatDate, formatMinutes } from './dates';
import { recurrenceLabel, statusLabel } from './labels';
import { describe, expect, test } from 'vitest';

describe('date and duration formatting', () => {
  test('formats date-only values without timezone conversion', () => {
    expect(formatDate('2025-01-02')).toBe('02/01/2025');
    expect(formatDate('')).toBe('');
  });

  test('formats minutes as hours and minutes', () => {
    expect(formatMinutes(0)).toBe('0m');
    expect(formatMinutes(125)).toBe('2h 5m');
    expect(formatMinutes(120)).toBe('2h');
    expect(formatMinutes(null)).toBe('');
  });
});

describe('task labels', () => {
  test('uses friendly status labels and preserves unknown values', () => {
    expect(statusLabel('In_progress')).toBe('In progress');
    expect(statusLabel('Archived')).toBe('Archived');
  });

  test('describes recurrence frequency and interval', () => {
    expect(recurrenceLabel('weekly', 1)).toBe('Repeats weekly');
    expect(recurrenceLabel('monthly', 3)).toBe('Every 3 × monthly');
    expect(recurrenceLabel('', 1)).toBe('');
  });
});
