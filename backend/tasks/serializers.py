from django.db.models import Q
from rest_framework import serializers

from tasks.models import Category, Tag, Task
from tasks.services import get_task_service


class OwnedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Chỉ cho chọn đối tượng thuộc user hiện tại (và dùng chung nếu allow_shared)."""

    def __init__(self, *, allow_shared=False, **kwargs):
        self.allow_shared = allow_shared
        super().__init__(**kwargs)

    def get_queryset(self):
        user = self.context['request'].user
        owned = Q(owner=user)
        if self.allow_shared:
            owned |= Q(owner__isnull=True)
        return self.queryset.model.objects.filter(owned)


class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'is_default', 'task_count']
        read_only_fields = ['slug', 'created_at', 'is_default']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Name must not be blank.')
        user = self.context['request'].user
        clash = Category.objects.filter(Q(owner=user) | Q(owner__isnull=True), name__iexact=value)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value


class TagSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at', 'task_count']
        read_only_fields = ['created_at']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Name must not be blank.')
        clash = Tag.objects.filter(owner=self.context['request'].user, name__iexact=value)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError('A tag with this name already exists.')
        return value


class TagBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'priority', 'due_date', 'completed_at']


class TaskSerializer(serializers.ModelSerializer):
    category = OwnedPrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_shared=True, required=False, allow_null=True
    )
    tags = OwnedPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    parent = OwnedPrimaryKeyRelatedField(
        queryset=Task.objects.all(), required=False, allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    tags_detail = TagBriefSerializer(source='tags', many=True, read_only=True)
    subtask_count = serializers.IntegerField(read_only=True, default=0)
    subtasks_done = serializers.IntegerField(read_only=True, default=0)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'estimated_minutes', 'is_important',
            'category', 'category_name', 'tags', 'tags_detail',
            'parent', 'subtask_count', 'subtasks_done',
            'recurrence_frequency', 'recurrence_interval', 'recurrence_until',
            'archived_at', 'completed_at', 'created_at', 'updated_at', 'is_overdue',
        ]
        read_only_fields = ['archived_at', 'completed_at', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Title must not be blank.')
        return value

    def create(self, validated_data):
        return get_task_service().create(self.context['request'].user, validated_data)

    def update(self, instance, validated_data):
        return get_task_service().update(instance, validated_data)


class TaskDetailSerializer(TaskSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['subtasks']


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)


class BulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, max_length=500
    )
    action = serializers.CharField()
    priority = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False, allow_null=True)
