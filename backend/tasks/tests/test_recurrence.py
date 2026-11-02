from datetime import date

from django.test import SimpleTestCase

from tasks.domain.recurrence import (
    RecurrenceRegistry, RecurrenceRule, build_default_registry,
)


class RecurrenceRuleTests(SimpleTestCase):
    def setUp(self):
        self.registry = build_default_registry()

    def next(self, key, start, interval=1):
        return self.registry.get(key).next_date(start, interval)

    def test_daily_and_weekly(self):
        self.assertEqual(self.next('daily', date(2025, 12, 31), 3), date(2026, 1, 3))
        self.assertEqual(self.next('weekly', date(2025, 1, 1), 2), date(2025, 1, 15))

    def test_monthly_clamps_to_month_end(self):
        self.assertEqual(self.next('monthly', date(2025, 1, 31)), date(2025, 2, 28))
        self.assertEqual(self.next('monthly', date(2024, 1, 31)), date(2024, 2, 29))
        self.assertEqual(self.next('monthly', date(2025, 11, 30), 3), date(2026, 2, 28))

    def test_yearly_handles_leap_day(self):
        self.assertEqual(self.next('yearly', date(2024, 2, 29)), date(2025, 2, 28))
        self.assertEqual(self.next('yearly', date(2024, 2, 29), 4), date(2028, 2, 29))

    def test_registry_is_open_for_extension(self):
        class Biweekly(RecurrenceRule):
            key = 'biweekly'
            label = 'Every two weeks'

            def next_date(self, current, interval):
                return date.fromordinal(current.toordinal() + 14 * interval)

        registry = RecurrenceRegistry()
        registry.register(Biweekly())
        self.assertEqual(registry.get('biweekly').next_date(date(2025, 1, 1), 1), date(2025, 1, 15))
        self.assertIsNone(registry.get('daily'))
