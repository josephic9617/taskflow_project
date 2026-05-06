from rest_framework import status
from rest_framework.test import APITestCase

from .models import Board, Column, Task


class BoardApiTests(APITestCase):
    def test_seed_populates_empty_board(self):
        board = Board.objects.create(title='Roadmap')

        response = self.client.post(f'/api/boards/{board.id}/seed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        board.refresh_from_db()
        self.assertEqual(board.columns.count(), 4)
        self.assertEqual(Task.objects.filter(column__board=board).count(), 8)
        self.assertEqual(response.data['title'], board.title)
        self.assertEqual(len(response.data['columns']), 4)

    def test_board_list_includes_task_count(self):
        board = Board.objects.create(title='Platform')
        column = Column.objects.create(board=board, title='To Do', order=0)
        Task.objects.create(column=column, title='Ship API', order=0)
        Task.objects.create(column=column, title='Review UI', order=1)

        response = self.client.get('/api/boards/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['task_count'], 2)


class TaskMoveApiTests(APITestCase):
    def test_move_reorders_tasks_in_target_column(self):
        board = Board.objects.create(title='Delivery')
        source = Column.objects.create(board=board, title='To Do', order=0)
        target = Column.objects.create(board=board, title='Done', order=1)
        task_a = Task.objects.create(column=target, title='Existing A', order=0)
        task_b = Task.objects.create(column=target, title='Existing B', order=1)
        moved_task = Task.objects.create(column=source, title='Moved', order=0)

        response = self.client.post(
            '/api/tasks/move/',
            {'task_id': moved_task.id, 'column_id': target.id, 'order': 1},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        moved_task.refresh_from_db()
        task_a.refresh_from_db()
        task_b.refresh_from_db()

        self.assertEqual(moved_task.column_id, target.id)
        self.assertEqual(task_a.order, 0)
        self.assertEqual(moved_task.order, 1)
        self.assertEqual(task_b.order, 2)
