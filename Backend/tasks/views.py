from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Category
from django.db.models import Q
from rest_framework.views import APIView


from .serializers import (
    TaskSerializer, 
    TaskListSerializer, 
    CategorySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet quản lý Category
    Hỗ trợ CRUD cho danh mục
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_fields = ['is_default']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']

    @action(detail=True, methods=['GET'])
    def tasks(self, request, pk=None):
        """
        Lấy danh sách tasks của một category cụ thể
        """
        category = self.get_object()
        tasks = category.tasks.all()
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet quản lý Task
    Hỗ trợ đầy đủ các thao tác CRUD
    """
    queryset = Task.objects.all()
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    # Lựa chọn serializer dựa trên action
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    # Các trường được phép lọc
    filterset_fields = [
        'status', 
        'priority', 
        'category', 
        'is_important'
    ]
    
    # Các trường được phép tìm kiếm
    search_fields = ['title', 'description']
    
    # Các trường được phép sắp xếp
    ordering_fields = [
        'created_at', 
        'due_date', 
        'priority'
    ]

    @action(detail=False, methods=['GET'])
    def overdue(self, request):
        """
        Lấy danh sách tasks quá hạn
        """
        overdue_tasks = Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        )

        # Kiểm tra nếu không có task nào quá hạn
        if not overdue_tasks.exists():
            return Response(
                {'message': 'No overdue tasks found.'},
                status=status.HTTP_200_OK
            )
    
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def change_status(self, request, pk=None):
        """
        Thay đổi trạng thái của task
        """
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response(
                {'error': 'Trạng thái không hợp lệ'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = new_status
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """
        Thống kê các task
        """
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        pending_tasks = Task.objects.filter(status='pending').count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        })

class TaskListView(APIView):
    def get(self, request):
        # Lấy các tham số từ query string (search, status, priority, due_date)
        search = request.query_params.get('search', '')
        status_filter = request.query_params.get('status', '')
        priority_filter = request.query_params.get('priority', '')
        due_date_filter = request.query_params.get('dueDate', '')

        # Xây dựng câu truy vấn với các bộ lọc
        tasks = Task.objects.all()

        if search:
            tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if status_filter:
            tasks = tasks.filter(status=status_filter)

        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)

        if due_date_filter:
            tasks = tasks.filter(due_date=due_date_filter)

        # Serialize và trả về kết quả
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
    