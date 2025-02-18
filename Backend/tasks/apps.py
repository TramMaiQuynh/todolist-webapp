from django.apps import AppConfig
from django.db.models.signals import post_migrate

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        from tasks.models import Category
        post_migrate.connect(create_default_categories, sender=self)

def create_default_categories(sender, **kwargs):
    from tasks.models import Category
    if not Category.objects.exists():
        Category.create_default_categories()