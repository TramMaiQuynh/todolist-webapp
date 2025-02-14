from rest_framework import serializers
from .models import Task, Category

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer cho model Category
    Cho phép chuyển đổi Category sang JSON và ngược lại
    """
    # Số lượng tasks thuộc category
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 
            'name', 
            'slug', 
            'created_at', 
            'is_default', 
            'task_count'
        ]
        read_only_fields = ['slug', 'created_at']

    def get_task_count(self, obj):
        """
        Phương thức tùy chỉnh để đếm số lượng tasks trong mỗi category
        """
        return obj.tasks.count()

# class TaskSerializer(serializers.ModelSerializer):
#     """
#     Serializer cho model Task
#     Hỗ trợ đầy đủ các thao tác CRUD
#     """
#     # Thêm serializer nested cho category
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), 
#         source='category', 
#         write_only=True,
#         required=False
#     )
    
#     # Custom field để cho phép tạo category mới
#     custom_category = serializers.CharField(
#         write_only=True, 
#         required=False, 
#         allow_blank=True
#     )

#     class Meta:
#         model = Task
#         fields = [
#             'id', 
#             'title', 
#             'description', 
#             'status', 
#             'priority',
#             'created_at', 
#             'updated_at', 
#             'due_date', 
#             'completed_at', 
#             'category', 
#             'category_id',
#             'custom_category',
#             'is_important',
#             'is_overdue'
#         ]
#         read_only_fields = [
#             'created_at', 
#             'updated_at', 
#             'completed_at'
#         ]

#     # def create(self, validated_data):
#     #     """
#     #     Ghi đè phương thức create để không tạo category mới vào database
#     #     """
#     #     custom_category = validated_data.pop('custom_category ', None)
        
#     #     if custom_category:
#     #         # Kiểm tra xem custom_category có tồn tại trong database không
#     #         category = Category.objects.filter(name=custom_category).first()
            
#     #         if category:
#     #             # Nếu đã có category trong database, sử dụng category đó
#     #             validated_data['category'] = category
#     #         else:
#     #             # Nếu custom_category không có trong database, chỉ gán tên này cho task mà không tạo mới category
#     #             validated_data['category'] = None  # Hoặc bạn có thể để nó là category mặc định

#     #     # Tạo task mà không tạo mới category
#     #     return super().create(validated_data)

#     def to_representation(self, instance):
#         """
#         Phương thức tùy chỉnh để thêm trường is_overdue
#         """
#         rep = super().to_representation(instance)
#         rep['is_overdue'] = instance.is_overdue()
#         return rep

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Task
    Hỗ trợ đầy đủ các thao tác CRUD
    """
    # category = CategorySerializer(read_only=True)  # Still serialize category as an object for read operations

    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'status', 
            'priority',
            'created_at', 
            'updated_at', 
            'due_date', 
            'completed_at', 
            'category',  # The category will just be serialized when reading
            'is_important',
            'is_overdue'
        ]
        read_only_fields = [
            'created_at', 
            'updated_at', 
            'completed_at'
        ]

    def to_representation(self, instance):
        """
        Custom method to add is_overdue field
        """
        rep = super().to_representation(instance)
        rep['is_overdue'] = instance.is_overdue()  # Add is_overdue to the response
        return rep


class TaskListSerializer(TaskSerializer):
    """
    Serializer dành riêng cho list view
    Giảm thiểu thông tin chi tiết để tối ưu hiệu năng
    """
    class Meta(TaskSerializer.Meta):
        fields = [
            'id', 
            'title', 
            'status', 
            'priority', 
            'due_date', 
            'category', 
            'is_important',
            'is_overdue'
        ]
        

        