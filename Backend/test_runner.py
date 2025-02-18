# filepath: /home/quynh-tram/SgodUTH/ToDoList-WebApp/Backend/test_runner.py
from django.test.runner import DiscoverRunner
from django.core.management import call_command

class CustomTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)
        call_command('migrate', verbosity=1, interactive=False, database='test')
        return result