from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

from .models import Board, Column, Task
from .serializers import (
    BoardSerializer, BoardListSerializer,
    ColumnSerializer, TaskSerializer, TaskMoveSerializer,
)


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        return BoardSerializer

    @action(detail=True, methods=['post'], url_path='seed')
    def seed(self, request, pk=None):
        """Seed a board with default columns and sample tasks."""
        board = self.get_object()
        if board.columns.exists():
            return Response({'detail': 'Board already has columns.'}, status=400)

        defaults = [
            {'title': 'To Do', 'color': '#6366f1', 'tasks': [
                {'title': 'Design wireframes', 'priority': 'high', 'label': 'design', 'description': 'Create initial wireframes for the dashboard.'},
                {'title': 'Set up CI/CD pipeline', 'priority': 'medium', 'label': 'feature', 'description': 'Configure GitHub Actions for automated deployment.'},
                {'title': 'Write API documentation', 'priority': 'low', 'label': 'docs', 'description': 'Document all REST endpoints with examples.'},
            ]},
            {'title': 'In Progress', 'color': '#f59e0b', 'tasks': [
                {'title': 'Build task board UI', 'priority': 'urgent', 'label': 'feature', 'description': 'Implement Kanban board with drag-and-drop.'},
                {'title': 'WebSocket integration', 'priority': 'high', 'label': 'improvement', 'description': 'Real-time sync across all connected clients.'},
            ]},
            {'title': 'In Review', 'color': '#8b5cf6', 'tasks': [
                {'title': 'User authentication flow', 'priority': 'medium', 'label': 'feature', 'description': 'Login, register and JWT token management.'},
            ]},
            {'title': 'Done', 'color': '#10b981', 'tasks': [
                {'title': 'Project setup', 'priority': 'low', 'label': 'feature', 'description': 'Initialize Django + Vue project structure.'},
                {'title': 'Database schema design', 'priority': 'medium', 'label': 'research', 'description': 'Design Board, Column, Task relationships.'},
            ]},
        ]

        with transaction.atomic():
            for col_idx, col_data in enumerate(defaults):
                column = Column.objects.create(
                    board=board,
                    title=col_data['title'],
                    color=col_data['color'],
                    order=col_idx,
                )
                for task_idx, task_data in enumerate(col_data['tasks']):
                    Task.objects.create(
                        column=column,
                        order=task_idx,
                        **task_data,
                    )

        serializer = BoardSerializer(board)
        return Response(serializer.data)


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'], url_path='move')
    def move(self, request):
        """Move a task to a new column/position. Broadcasts via WebSocket."""
        serializer = TaskMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = serializer.validated_data['task_id']
        column_id = serializer.validated_data['column_id']
        new_order = serializer.validated_data['order']

        try:
            task = Task.objects.get(pk=task_id)
            column = Column.objects.get(pk=column_id)
        except (Task.DoesNotExist, Column.DoesNotExist):
            return Response({'detail': 'Task or Column not found.'}, status=status.HTTP_404_NOT_FOUND)

        board_id = str(column.board_id)

        with transaction.atomic():
            # Re-order tasks in target column
            tasks_in_col = list(
                Task.objects.filter(column=column)
                .exclude(pk=task_id)
                .order_by('order')
            )
            # Insert at new_order position
            tasks_in_col.insert(new_order, task)
            task.column = column
            for idx, t in enumerate(tasks_in_col):
                t.order = idx
                t.save(update_fields=['order', 'column'])

        # Broadcast to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'board_{board_id}',
            {
                'type': 'task_moved',
                'task_id': str(task_id),
                'column_id': str(column_id),
                'order': new_order,
            }
        )

        return Response(TaskSerializer(task).data)
