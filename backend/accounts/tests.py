from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from tasks.models import Task

User = get_user_model()
PASSWORD = 'Str0ng-Passw0rd!'


class AuthApiTests(APITestCase):
    def register(self, **overrides):
        data = {'username': 'alice', 'email': 'alice@example.com', 'password': PASSWORD,
                **overrides}
        return self.client.post('/api/v1/auth/register/', data)

    def login(self, login='alice', password=PASSWORD):
        return self.client.post('/api/v1/auth/login/', {'login': login, 'password': password})

    def test_register_login_me_logout_flow(self):
        res = self.register()
        self.assertEqual(res.status_code, 201, res.data)
        self.assertNotIn('password', res.data['user'])

        login = self.login()
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        self.assertEqual(self.client.get('/api/v1/auth/me/').data['username'], 'alice')

        self.assertEqual(self.client.post('/api/v1/auth/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/v1/auth/me/').status_code, 401)

    def test_login_with_email(self):
        self.register()
        self.assertEqual(self.login('ALICE@example.com').status_code, 200)

    def test_wrong_password_is_rejected_without_hint(self):
        self.register()
        wrong = self.login(password='nope')
        ghost = self.login('ghost', 'nope')
        self.assertEqual(wrong.status_code, 400)
        self.assertEqual(wrong.data, ghost.data)

    def test_register_validation(self):
        self.register()
        self.assertEqual(self.register(email='other@example.com').status_code, 400)
        self.assertEqual(self.register(username='b', email='ALICE@example.com').status_code, 400)
        self.assertEqual(
            self.register(username='c', email='c@example.com', password='123').status_code, 400)
        self.assertEqual(self.register(username='d', email='bad').status_code, 400)

    def test_login_revokes_previous_token(self):
        self.register()
        first = self.login().data['token']
        self.login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {first}')
        self.assertEqual(self.client.get('/api/v1/auth/me/').status_code, 401)

    def test_expired_token_is_rejected(self):
        user = User.objects.create_user('old', 'old@example.com', PASSWORD)
        token = Token.objects.create(user=user)
        Token.objects.filter(pk=token.pk).update(created=timezone.now() - timedelta(days=15))
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(self.client.get('/api/v1/auth/me/').status_code, 401)

    def test_change_password(self):
        self.register()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get().key)
        url = '/api/v1/auth/change-password/'
        bad = self.client.post(url, {'old_password': 'x', 'new_password': PASSWORD + '1'})
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post(url, {'old_password': PASSWORD, 'new_password': 'An0ther-Passw0rd!'})
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(User.objects.get().check_password('An0ther-Passw0rd!'))

    def test_delete_account_removes_data(self):
        self.register()
        Task.objects.create(owner=User.objects.get(), title='x')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get().key)
        self.assertEqual(self.client.delete('/api/v1/auth/me/').status_code, 204)
        self.assertFalse(User.objects.exists() or Task.objects.exists())
