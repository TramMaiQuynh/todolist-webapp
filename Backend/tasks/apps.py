from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Tạo các category mặc định khi ứng dụng bắt đầu
        from tasks.models import Category
        Category.create_default_categories()


