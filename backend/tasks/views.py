from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response

from tasks import selectors
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.serializers import (
    BulkActionSerializer,
    CategorySerializer,
    ChangeStatusSerializer,
    TagSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)
from tasks.services import get_task_service
from tasks.statistics import StatsContext, build_default_metric_registry


class OwnerCanModify(BasePermission):
    """Đối tượng dùng chung (owner=None) chỉ đọc; còn lại chỉ chủ sở hữu mới sửa/xóa."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.owner_id == request.user.id


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [*viewsets.ModelViewSet.permission_classes, OwnerCanModify]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return selectors.categories_for(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        return selectors.tags_for(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    filterset_class = TaskFilter
    filter_backends = [*viewsets.ModelViewSet.filter_backends, filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'completed_at', 'title',
                       'priority_rank']

    def filter_queryset(self, queryset):
        # Thêm id làm tie-breaker để phân trang ổn định khi nhiều dòng trùng giá trị sắp xếp
        queryset = super().filter_queryset(queryset)
        return queryset.order_by(*queryset.query.order_by, '-id')

    def get_serializer_class(self):
        return TaskDetailSerializer if self.action == 'retrieve' else TaskSerializer

    def get_queryset(self):
        queryset = selectors.tasks_for(self.request.user)
        # Danh sách mặc định ẩn task đã lưu trữ, trừ khi client chỉ định ?archived=
        if self.action == 'list' and 'archived' not in self.request.query_params:
            queryset = queryset.filter(archived_at__isnull=True)
        return queryset

    def _respond_with(self, task, status_code=status.HTTP_200_OK):
        task = self.get_queryset().get(pk=task.pk)
        return Response(TaskSerializer(task, context=self.get_serializer_context()).data,
                        status=status_code)

    @action(detail=True, methods=['post', 'patch'])
    def change_status(self, request, pk=None):
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = get_task_service().change_status(self.get_object(), serializer.validated_data['status'])
        return self._respond_with(task)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        return self._respond_with(get_task_service().archive(self.get_object()))

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        return self._respond_with(get_task_service().restore(self.get_object()))

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        params = {k: data[k] for k in ('priority', 'category') if k in data}
        result = get_task_service().bulk(request.user, data['ids'], data['action'], params)
        return Response(result)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        try:
            days = int(request.query_params.get('days', 30))
        except ValueError:
            raise ValidationError({'days': ['Must be an integer.']})
        if not 1 <= days <= 365:
            raise ValidationError({'days': ['Must be between 1 and 365.']})

        all_tasks = Task.objects.filter(owner=request.user)
        ctx = StatsContext(
            all_tasks=all_tasks,
            active_tasks=all_tasks.filter(archived_at__isnull=True),
            today=timezone.localdate(),
            days=days,
        )
        return Response({
            'generated_at': timezone.now().isoformat(),
            'today': ctx.today.isoformat(),
            **build_default_metric_registry().compute_all(ctx),
        })

    @action(detail=False, methods=['get'])
    def meta(self, request):
        """Các giá trị hợp lệ để frontend dựng form mà không phải hard-code."""
        service = get_task_service()
        return Response({
            'statuses': [{'key': k, 'label': v} for k, v in Task.STATUS_CHOICES],
            'priorities': [{'key': k, 'label': v} for k, v in Task.PRIORITY_CHOICES],
            'recurrences': service.recurrence.choices(),
            'bulk_actions': service.bulk_actions.names(),
        })
