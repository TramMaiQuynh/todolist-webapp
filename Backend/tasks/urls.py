from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet

# Tạo router cho ViewSets
router = DefaultRouter()

# Đăng ký các ViewSet
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Đường dẫn chính của API
    path('api/v1/', include(router.urls)),

    
    
    # Endpoint tùy chỉnh (nếu cần)
    # Ví dụ: path('api/v1/tasks/overdue/', TaskViewSet.as_view({'get': 'overdue'}), name='task-overdue'),
]

# Các endpoint sẽ được tạo ra:
# GET    /api/v1/tasks/           - Danh sách tasks
# POST   /api/v1/tasks/           - Tạo task mới
# GET    /api/v1/tasks/{id}/      - Chi tiết task
# PUT    /api/v1/tasks/{id}/      - Cập nhật toàn bộ task
# PATCH  /api/v1/tasks/{id}/      - Cập nhật một phần task
# DELETE /api/v1/tasks/{id}/      - Xóa task

# Các custom actions:
# GET    /api/v1/tasks/overdue/   - Danh sách tasks quá hạn
# GET    /api/v1/tasks/statistics/ - Thống kê tasks
# PATCH  /api/v1/tasks/{id}/change_status/ - Thay đổi trạng thái task

# Tương tự cho Categories