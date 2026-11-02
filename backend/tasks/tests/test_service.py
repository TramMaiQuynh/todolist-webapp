from django.test import TestCase
from django.utils import timezone

from tasks.domain.status import StatusTransitionPolicy
from tasks.exceptions import DomainError, InvalidTransition
from tasks.models import Category, Tag, Task
from tasks.tests.helpers import days_from_today, make_task, make_user, service_at, today


class TaskServiceTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.service = service_at(today())

    # --- tạo / validate
    def test_create_rejects_past_due_date(self):
        with self.assertRaises(DomainError) as ctx:
            self.service.create(self.user, {'title': 'x', 'due_date': days_from_today(-1)})
        self.assertEqual(ctx.exception.field, 'due_date')

    def test_create_as_completed_is_rejected(self):
        with self.assertRaises(DomainError):
            self.service.create(self.user, {'title': 'x', 'status': Task.COMPLETED})

    def test_create_sets_tags(self):
        tag = Tag.objects.create(owner=self.user, name='home')
        task = self.service.create(self.user, {'title': 'x', 'tags': [tag]})
        self.assertEqual(list(task.tags.all()), [tag])

    def test_updating_other_fields_of_overdue_task_is_allowed(self):
        task = make_task(self.user, due_date=days_from_today(-5))
        self.service.update(task, {'title': 'renamed', 'due_date': task.due_date})
        task.refresh_from_db()
        self.assertEqual(task.title, 'renamed')

    def test_moving_due_date_into_the_past_is_rejected(self):
        task = make_task(self.user, due_date=days_from_today(3))
        with self.assertRaises(DomainError):
            self.service.update(task, {'due_date': days_from_today(-1)})

    # --- trạng thái
    def test_complete_sets_completed_at_and_reopen_clears_it(self):
        task = make_task(self.user)
        self.service.change_status(task, Task.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.service.change_status(task, Task.PENDING)
        self.assertIsNone(task.completed_at)

    def test_invalid_status_value(self):
        with self.assertRaises(DomainError):
            self.service.change_status(make_task(self.user), 'Nope')

    def test_policy_blocks_disallowed_transition(self):
        service = service_at(today())
        service.transitions = StatusTransitionPolicy({Task.PENDING: set()})
        with self.assertRaises(InvalidTransition):
            service.change_status(make_task(self.user), Task.COMPLETED)

    def test_update_with_status_goes_through_transition(self):
        task = make_task(self.user)
        self.service.update(task, {'status': Task.COMPLETED})
        self.assertIsNotNone(task.completed_at)

    # --- subtasks
    def test_subtask_rules(self):
        parent = make_task(self.user, title='parent')
        child = self.service.create(self.user, {'title': 'child', 'parent': parent})
        with self.assertRaises(DomainError):  # lồng quá 1 cấp
            self.service.create(self.user, {'title': 'grandchild', 'parent': child})
        with self.assertRaises(DomainError):  # tự làm cha của chính mình
            self.service.update(parent, {'parent': parent})
        other = make_task(self.user, title='other')
        with self.assertRaises(DomainError):  # task đã có con không thể thành con
            self.service.update(parent, {'parent': other})

    def test_parent_of_another_user_is_rejected(self):
        stranger_task = make_task(make_user('bob'))
        with self.assertRaises(DomainError):
            self.service.create(self.user, {'title': 'x', 'parent': stranger_task})

    def test_completing_parent_completes_subtasks(self):
        parent = make_task(self.user)
        child = make_task(self.user, parent=parent)
        self.service.change_status(parent, Task.COMPLETED)
        child.refresh_from_db()
        self.assertEqual(child.status, Task.COMPLETED)

    def test_reopening_subtask_reopens_completed_parent(self):
        parent = make_task(self.user)
        child = make_task(self.user, parent=parent)
        self.service.change_status(parent, Task.COMPLETED)
        child.refresh_from_db()
        self.service.change_status(child, Task.PENDING)
        parent.refresh_from_db()
        self.assertEqual(parent.status, Task.IN_PROGRESS)

    # --- recurrence
    def test_recurrence_validation(self):
        with self.assertRaises(DomainError):  # cần due_date
            self.service.create(self.user, {'title': 'x', 'recurrence_frequency': 'daily'})
        with self.assertRaises(DomainError):  # quy tắc không tồn tại
            self.service.create(self.user, {
                'title': 'x', 'due_date': days_from_today(1), 'recurrence_frequency': 'hourly'})
        with self.assertRaises(DomainError):  # interval sai
            self.service.create(self.user, {
                'title': 'x', 'due_date': days_from_today(1),
                'recurrence_frequency': 'daily', 'recurrence_interval': 0})

    def test_completing_recurring_task_spawns_next_once(self):
        tag = Tag.objects.create(owner=self.user, name='gym')
        task = self.service.create(self.user, {
            'title': 'Workout', 'due_date': days_from_today(1), 'priority': 'High',
            'recurrence_frequency': 'weekly', 'tags': [tag]})
        self.service.change_status(task, Task.COMPLETED)
        nxt = Task.objects.exclude(pk=task.pk).get()
        self.assertEqual(nxt.due_date, days_from_today(8))
        self.assertEqual((nxt.status, nxt.priority), (Task.PENDING, 'High'))
        self.assertEqual(list(nxt.tags.all()), [tag])
        # đổi qua lại không sinh thêm bản mới khi chưa hoàn thành lại
        self.service.change_status(task, Task.PENDING)
        self.assertEqual(Task.objects.count(), 2)

    def test_late_completion_skips_missed_occurrences(self):
        task = make_task(self.user, due_date=days_from_today(-10),
                         recurrence_frequency='daily', recurrence_interval=1)
        self.service.change_status(task, Task.COMPLETED)
        nxt = Task.objects.exclude(pk=task.pk).get()
        self.assertEqual(nxt.due_date, today())

    def test_recurrence_stops_after_until(self):
        task = make_task(self.user, due_date=days_from_today(1), recurrence_frequency='daily',
                         recurrence_until=days_from_today(1))
        self.service.change_status(task, Task.COMPLETED)
        self.assertEqual(Task.objects.count(), 1)

    # --- archive
    def test_archive_and_restore_cascade_to_subtasks(self):
        parent = make_task(self.user)
        child = make_task(self.user, parent=parent)
        self.service.archive(parent)
        child.refresh_from_db()
        self.assertTrue(parent.is_archived and child.is_archived)
        self.service.restore(parent)
        child.refresh_from_db()
        self.assertFalse(parent.is_archived or child.is_archived)

    def test_restore_keeps_subtasks_archived_before_parent(self):
        parent = make_task(self.user)
        child = make_task(self.user, parent=parent, archived_at=timezone.now())
        original_archive_time = child.archived_at
        self.service.archive(parent)
        child.refresh_from_db()
        self.assertEqual(child.archived_at, original_archive_time)
        self.service.restore(parent)
        child.refresh_from_db()
        self.assertEqual(child.archived_at, original_archive_time)

    # --- bulk
    def test_bulk_only_touches_owned_tasks(self):
        mine = make_task(self.user)
        theirs = make_task(make_user('bob'))
        result = self.service.bulk(self.user, [mine.pk, theirs.pk], 'complete')
        mine.refresh_from_db()
        theirs.refresh_from_db()
        self.assertEqual(result, {'requested': 2, 'affected': 1})
        self.assertEqual((mine.status, theirs.status), (Task.COMPLETED, Task.PENDING))

    def test_bulk_set_priority_and_category(self):
        task = make_task(self.user)
        category = Category.objects.create(owner=self.user, name='Mine')
        self.service.bulk(self.user, [task.pk], 'set_priority', {'priority': 'High'})
        self.service.bulk(self.user, [task.pk], 'set_category', {'category': category.pk})
        task.refresh_from_db()
        self.assertEqual((task.priority, task.category), ('High', category))

    def test_bulk_rejects_unknown_action_and_foreign_category(self):
        task = make_task(self.user)
        with self.assertRaises(DomainError):
            self.service.bulk(self.user, [task.pk], 'explode')
        foreign = Category.objects.create(owner=make_user('bob'), name='Bobs')
        with self.assertRaises(DomainError):
            self.service.bulk(self.user, [task.pk], 'set_category', {'category': foreign.pk})

    def test_bulk_delete(self):
        task = make_task(self.user)
        self.service.bulk(self.user, [task.pk], 'delete')
        self.assertFalse(Task.objects.exists())
