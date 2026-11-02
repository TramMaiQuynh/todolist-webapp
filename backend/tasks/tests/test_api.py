from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from tasks.models import Category, Tag, Task
from tasks.tests.helpers import days_from_today, make_task, make_user

TASKS = '/api/v1/tasks/'


class ApiBase(APITestCase):
    def setUp(self):
        self.user = make_user('alice')
        self.other = make_user('bob')
        self.login(self.user)

    def login(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')


class AuthRequiredTests(APITestCase):
    def test_endpoints_reject_anonymous(self):
        for url in (TASKS, '/api/v1/categories/', '/api/v1/tags/', TASKS + 'statistics/'):
            self.assertEqual(self.client.get(url).status_code, 401, url)


class TaskApiTests(ApiBase):
    def test_create_and_list(self):
        res = self.client.post(TASKS, {'title': '  Buy milk  ', 'due_date': str(days_from_today(2))})
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['title'], 'Buy milk')
        self.assertEqual(self.client.get(TASKS).data['count'], 1)

    def test_blank_title_and_past_due_date(self):
        self.assertEqual(self.client.post(TASKS, {'title': '   '}).status_code, 400)
        res = self.client.post(TASKS, {'title': 'x', 'due_date': str(days_from_today(-1))})
        self.assertEqual(res.status_code, 400)
        self.assertIn('due_date', res.data)

    def test_users_cannot_see_or_touch_each_others_tasks(self):
        theirs = make_task(self.other, title='secret')
        self.assertEqual(self.client.get(TASKS).data['count'], 0)
        self.assertEqual(self.client.get(f'{TASKS}{theirs.pk}/').status_code, 404)
        self.assertEqual(self.client.patch(f'{TASKS}{theirs.pk}/', {'title': 'x'}).status_code, 404)
        self.assertEqual(self.client.delete(f'{TASKS}{theirs.pk}/').status_code, 404)
        self.assertTrue(Task.objects.filter(pk=theirs.pk).exists())

    def test_cannot_use_other_users_category_tag_or_parent(self):
        cat = Category.objects.create(owner=self.other, name='Bobs')
        tag = Tag.objects.create(owner=self.other, name='bobtag')
        theirs = make_task(self.other)
        self.assertEqual(self.client.post(TASKS, {'title': 'x', 'category': cat.pk}).status_code, 400)
        self.assertEqual(self.client.post(TASKS, {'title': 'x', 'tags': [tag.pk]}).status_code, 400)
        self.assertEqual(self.client.post(TASKS, {'title': 'x', 'parent': theirs.pk}).status_code, 400)

    def test_default_category_is_usable(self):
        work = Category.objects.get(name='Work', owner__isnull=True)
        res = self.client.post(TASKS, {'title': 'x', 'category': work.pk})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['category_name'], 'Work')

    def test_filters(self):
        make_task(self.user, title='a', status=Task.COMPLETED, priority='Low')
        make_task(self.user, title='b', priority='High', is_important=True,
                  due_date=days_from_today(-2))
        make_task(self.user, title='c', priority='High', due_date=days_from_today(5))

        def titles(query):
            res = self.client.get(f'{TASKS}?{query}')
            self.assertEqual(res.status_code, 200, res.data)
            return sorted(t['title'] for t in res.data['results'])

        self.assertEqual(titles('status=Completed'), ['a'])
        self.assertEqual(titles('status=Pending,Completed'), ['a', 'b', 'c'])
        self.assertEqual(titles('priority=High'), ['b', 'c'])
        self.assertEqual(titles('is_important=true'), ['b'])
        self.assertEqual(titles('overdue=true'), ['b'])
        self.assertEqual(titles('overdue=false'), ['a', 'c'])
        self.assertEqual(titles(f'due_before={days_from_today(0)}'), ['b'])
        self.assertEqual(titles('search=c'), ['c'])

    def test_completed_task_is_not_overdue(self):
        make_task(self.user, status=Task.COMPLETED, due_date=days_from_today(-3))
        res = self.client.get(TASKS)
        self.assertFalse(res.data['results'][0]['is_overdue'])

    def test_ordering_by_priority_rank(self):
        for p in ('Low', 'High', 'Medium'):
            make_task(self.user, title=p, priority=p)
        res = self.client.get(f'{TASKS}?ordering=-priority_rank')
        self.assertEqual([t['title'] for t in res.data['results']], ['High', 'Medium', 'Low'])

    def test_pagination(self):
        for i in range(25):
            make_task(self.user, title=f't{i}')
        res = self.client.get(TASKS)
        self.assertEqual((res.data['count'], len(res.data['results'])), (25, 20))
        self.assertEqual(len(self.client.get(f'{TASKS}?page_size=5').data['results']), 5)

    def test_change_status_endpoint(self):
        task = make_task(self.user)
        res = self.client.patch(f'{TASKS}{task.pk}/change_status/', {'status': 'Completed'})
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.data['completed_at'])
        bad = self.client.patch(f'{TASKS}{task.pk}/change_status/', {'status': 'Bogus'})
        self.assertEqual(bad.status_code, 400)

    def test_patch_status_completes_via_service(self):
        task = make_task(self.user, due_date=days_from_today(1), recurrence_frequency='daily')
        self.client.patch(f'{TASKS}{task.pk}/', {'status': 'Completed'})
        self.assertEqual(Task.objects.count(), 2)

    def test_archive_hides_from_default_list_and_restore_brings_back(self):
        task = make_task(self.user)
        self.assertEqual(self.client.post(f'{TASKS}{task.pk}/archive/').status_code, 200)
        self.assertEqual(self.client.get(TASKS).data['count'], 0)
        self.assertEqual(self.client.get(f'{TASKS}?archived=true').data['count'], 1)
        self.assertEqual(self.client.get(f'{TASKS}?archived=all').data['count'], 1)
        self.client.post(f'{TASKS}{task.pk}/restore/')
        self.assertEqual(self.client.get(TASKS).data['count'], 1)

    def test_detail_includes_subtasks_and_list_counts_them(self):
        parent = make_task(self.user, title='p')
        make_task(self.user, title='c1', parent=parent, status=Task.COMPLETED)
        make_task(self.user, title='c2', parent=parent)
        detail = self.client.get(f'{TASKS}{parent.pk}/').data
        self.assertEqual(len(detail['subtasks']), 2)
        row = next(iter(self.client.get(f'{TASKS}?top_level=true').data['results']))
        self.assertEqual((row['subtask_count'], row['subtasks_done']), (2, 1))

    def test_bulk_endpoint(self):
        a, b = make_task(self.user), make_task(self.user)
        res = self.client.post(TASKS + 'bulk/', {'ids': [a.pk, b.pk], 'action': 'complete'},
                               format='json')
        self.assertEqual(res.data, {'requested': 2, 'affected': 2})
        bad = self.client.post(TASKS + 'bulk/', {'ids': [a.pk], 'action': 'nope'}, format='json')
        self.assertEqual(bad.status_code, 400)
        empty = self.client.post(TASKS + 'bulk/', {'ids': [], 'action': 'complete'}, format='json')
        self.assertEqual(empty.status_code, 400)

    def test_meta_endpoint(self):
        data = self.client.get(TASKS + 'meta/').data
        self.assertIn('daily', [r['key'] for r in data['recurrences']])
        self.assertIn('complete', data['bulk_actions'])


class CategoryAndTagApiTests(ApiBase):
    def test_lists_defaults_plus_own_but_not_others(self):
        Category.objects.create(owner=self.user, name='Mine')
        Category.objects.create(owner=self.other, name='Bobs')
        names = {c['name'] for c in self.client.get('/api/v1/categories/').data['results']}
        self.assertIn('Work', names)
        self.assertIn('Mine', names)
        self.assertNotIn('Bobs', names)

    def test_create_category_rules(self):
        url = '/api/v1/categories/'
        self.assertEqual(self.client.post(url, {'name': 'Gym'}).status_code, 201)
        self.assertEqual(self.client.post(url, {'name': 'gym'}).status_code, 400)
        self.assertEqual(self.client.post(url, {'name': 'work'}).status_code, 400)
        self.login(self.other)
        self.assertEqual(self.client.post(url, {'name': 'Gym'}).status_code, 201)

    def test_default_category_is_read_only(self):
        work = Category.objects.get(name='Work', owner__isnull=True)
        url = f'/api/v1/categories/{work.pk}/'
        self.assertEqual(self.client.patch(url, {'name': 'X'}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_deleting_category_keeps_tasks(self):
        cat = Category.objects.create(owner=self.user, name='Temp')
        task = make_task(self.user, category=cat)
        self.assertEqual(self.client.delete(f'/api/v1/categories/{cat.pk}/').status_code, 204)
        task.refresh_from_db()
        self.assertIsNone(task.category)

    def test_tag_crud_and_isolation(self):
        res = self.client.post('/api/v1/tags/', {'name': 'urgent'})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.client.post('/api/v1/tags/', {'name': 'URGENT'}).status_code, 400)
        self.login(self.other)
        self.assertEqual(self.client.get('/api/v1/tags/').data['count'], 0)
        self.assertEqual(self.client.delete(f"/api/v1/tags/{res.data['id']}/").status_code, 404)

    def test_filter_tasks_by_tag(self):
        tag = Tag.objects.create(owner=self.user, name='t')
        tagged = make_task(self.user, title='tagged')
        tagged.tags.add(tag)
        make_task(self.user, title='plain')
        res = self.client.get(f'{TASKS}?tags={tag.pk}')
        self.assertEqual([t['title'] for t in res.data['results']], ['tagged'])
