from rest_framework import serializers
from .models import Board, Column, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = '__all__'


class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = '__all__'


class BoardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for board list (no nested data)."""
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'color', 'created_at', 'task_count']

    def get_task_count(self, obj):
        return Task.objects.filter(column__board=obj).count()


class TaskMoveSerializer(serializers.Serializer):
    """Serializer for drag-and-drop task moves."""
    task_id = serializers.UUIDField()
    column_id = serializers.UUIDField()
    order = serializers.IntegerField(min_value=0)
