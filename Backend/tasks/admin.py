from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Task, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Cấu hình quản lý Category trong admin
    """
    list_display = ['name', 'slug', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Cấu hình quản lý Task trong admin
    """
    list_display = [
        'title', 
        'description',
        'status', 
        'priority', 
        'category', 
        'due_date', 
        'is_important', 
        'is_overdue'
    ]
    list_filter = [
        'status', 
        'priority', 
        'category', 
        'is_important'
    ]
    search_fields = ['title', 'description']
    
    # Nhóm các trường theo từng phần
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'description', 'category')
        }),
        ('Trạng thái & Ưu tiên', {
            'fields': ('status', 'priority', 'is_important')
        }),
        ('Thời gian', {
            'fields': ('due_date', 'created_at', 'updated_at', 'completed_at')
        })
    )
    
    # Các trường chỉ đọc
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    def is_overdue(self, obj):
        """
        Hiển thị trạng thái quá hạn trong danh sách
        """
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Quá hạn'

    