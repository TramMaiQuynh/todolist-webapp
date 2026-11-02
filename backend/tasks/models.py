from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """
    Danh mục. owner = None nghĩa là danh mục mặc định dùng chung cho mọi user;
    ngược lại là danh mục riêng của user đó.
    """
    DEFAULT_CATEGORIES = [
        ('Work', 'Công việc'),
        ('Study', 'Học tập'),
        ('Personal', 'Cá nhân'),
        ('Health', 'Sức khỏe'),
        ('Finance', 'Tài chính'),
        ('Travel', 'Du lịch'),
        ('Family', 'Gia đình'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories',
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'], name='unique_category_name_per_owner'
            ),
            models.UniqueConstraint(
                fields=['name'],
                condition=Q(owner__isnull=True),
                name='unique_default_category_name',
            ),
        ]

    @classmethod
    def create_default_categories(cls):
        for name, _display in cls.DEFAULT_CATEGORIES:
            cls.objects.get_or_create(
                name=name,
                owner=None,
                defaults={'is_default': True, 'slug': slugify(name)},
            )


class Tag(models.Model):
    """Thẻ nhãn riêng của từng user, gắn nhiều thẻ cho một task."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tags'
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_tag_name_per_owner'),
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    # Giá trị trạng thái dùng ở nhiều nơi -> khai báo hằng để tránh "magic string"
    PENDING = 'Pending'
    IN_PROGRESS = 'In_progress'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    is_important = models.BooleanField(default=False)

    # Task con (chỉ 1 cấp, được kiểm tra ở service)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks'
    )

    # Lưu trữ mềm: archived_at != None nghĩa là đã lưu trữ
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by_parent = models.BooleanField(default=False, editable=False)

    # Lặp lại. Không dùng choices để thêm quy tắc mới (đăng ký ở RecurrenceRegistry)
    # không cần migration. Chuỗi rỗng = không lặp.
    recurrence_frequency = models.CharField(max_length=20, blank=True, default='')
    recurrence_interval = models.PositiveSmallIntegerField(default=1)
    recurrence_until = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # completed_at luôn phản ánh trạng thái hiện tại
        if self.status == self.COMPLETED:
            if not self.completed_at:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_archived(self):
        return self.archived_at is not None

    def is_overdue(self, today=None):
        today = today or timezone.localdate()
        return bool(self.due_date and self.status != self.COMPLETED and self.due_date < today)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at', 'title']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['owner', 'due_date']),
            models.Index(fields=['owner', 'archived_at']),
        ]
