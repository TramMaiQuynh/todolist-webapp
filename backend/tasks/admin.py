from django.contrib import admin

from .models import Category, Tag, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'priority', 'category', 'due_date',
                    'is_important', 'archived_at']
    list_filter = ['status', 'priority', 'is_important', 'category']
    search_fields = ['title', 'description', 'owner__username']
    raw_id_fields = ['owner', 'parent']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
