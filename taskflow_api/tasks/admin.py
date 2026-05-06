from django.contrib import admin
from .models import Board, Column, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'created_at']
    search_fields = ['title']


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'order']
    list_filter = ['board']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'column', 'priority', 'label', 'order', 'created_at']
    list_filter = ['priority', 'label', 'column__board']
    search_fields = ['title', 'description']
