from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Category(models.Model):
    DEFAULT_CATEGORIES = [
        ('Work', 'Công việc'),
        ('Study', 'Học tập'),
        ('Personal', 'Cá nhân'),
        ('Health', 'Sức khỏe'),
        ('Finance', 'Tài chính'),
        ('Travel', 'Du lịch'),
        ('Family', 'Gia đình')
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Tự động tạo slug từ tên
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Chỉ lưu nếu chưa tồn tại category với tên này
        if not Category.objects.filter(name=self.name).exists():
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    @classmethod
    def create_default_categories(cls):
        """
        Phương thức tạo các danh mục mặc định nếu chưa tồn tại
        """
        for category_name, category_display in cls.DEFAULT_CATEGORIES:
            cls.objects.get_or_create(
                name=category_name, 
                defaults={
                    'is_default': True,
                    'slug': slugify(category_name)
                }
            )

class Task(models.Model):
    # Các lựa chọn cho trạng thái công việc
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In_progress', 'In progress'),
        ('Completed', 'Completed')
    ]
    
    # Các lựa chọn cho mức độ ưu tiên công việc
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ]

    # Các trường trong bảng Task
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )

    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='Medium'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tasks'
    )
    
    custom_category = models.CharField(
        max_length=100, 
        null=True, 
        blank=True
    )

    is_important = models.BooleanField(default=False)

    def clean(self):
        # Validation cho ngày hết hạn
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError("The due date must be after the created day!")

    def save(self, *args, **kwargs):
        # Tự động cập nhật completed_at khi trạng thái chuyển sang completed
        if self.status == 'Completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Xử lý custom category
        if self.custom_category and not self.category:
            new_category, created = Category.objects.get_or_create(
                name=self.custom_category,
                defaults={
                    'is_default': False,
                    'slug': slugify(self.custom_category)
                }
            )
            self.category = new_category
            self.custom_category = None
        
        self.full_clean()  # Chạy validation
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Kiểm tra xem công việc có quá hạn không"""
        return (
            self.due_date and 
            self.due_date < timezone.now() and 
            self.status != 'completed'
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at', 'title']

