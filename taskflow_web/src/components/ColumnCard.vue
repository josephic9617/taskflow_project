<template>
  <div class="column-card" :style="{ borderTop: `3px solid ${column.color}` }">
    <!-- Header -->
    <div class="column-header" :class="{ selected: isSelected('column', column.id) }">
      <input type="checkbox" :checked="isSelected('column', column.id)" @click.stop="toggleSelect('column', column.id)" class="item-checkbox" />
      <div class="column-dot" :style="{ background: column.color }" />
      
      <div v-if="editingTitle" class="flex-1">
        <input
          v-model="newTitle"
          class="column-title-input"
          @blur="saveTitle"
          @keyup.enter="saveTitle"
          @keyup.escape="cancelEdit"
          autofocus
        />
      </div>
      <span v-else class="column-title" @click="startEdit">{{ column.title }}</span>
      
      <span class="column-count">{{ column.tasks.length }}</span>
      <button class="btn btn-icon btn-ghost btn-sm" @click="startEdit" title="Edit title" v-if="!editingTitle">✏️</button>
      <button class="btn btn-icon btn-ghost btn-sm" @click="$emit('delete-column', column.id)" title="Remove column">✕</button>
    </div>

    <!-- Task list with drag & drop -->
    <VueDraggable
      v-model="localTasks"
      :group="{ name: 'tasks', pull: true, put: true }"
      class="column-tasks"
      ghost-class="sortable-ghost"
      drag-class="sortable-drag"
      animation="200"
      :delay="60"
      @end="onDragEnd"
    >
      <TaskItem
        v-for="task in localTasks"
        :key="task.id"
        :task="task"
        :selected="isSelected('task', task.id)"
        @toggle-select="toggleSelect('task', task.id)"
        @edit="$emit('edit-task', task)"
        @delete="$emit('delete-task', $event)"
      />
    </VueDraggable>

    <!-- Footer -->
    <div class="column-footer">
      <button class="add-task-btn" @click="$emit('add-task', column.id)">
        <span style="font-size:16px;line-height:1">+</span> Add task
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import TaskItem from './TaskItem.vue'

const props = defineProps({
  column: Object,
  allColumns: Array,
  selectedItems: Array,
})
const emit = defineEmits(['add-task', 'edit-task', 'delete-task', 'delete-column', 'task-moved', 'update-column', 'toggle-select'])

function isSelected(type, id) {
  return props.selectedItems?.some(item => item.type === type && item.id === id)
}
function toggleSelect(type, id) {
  emit('toggle-select', { type, id })
}

// --- Inline Edit Title ---
const editingTitle = ref(false)
const newTitle = ref(props.column.title)

function startEdit() {
  newTitle.value = props.column.title
  editingTitle.value = true
}
function cancelEdit() {
  editingTitle.value = false
}
function saveTitle() {
  if (!newTitle.value.trim() || newTitle.value === props.column.title) {
    editingTitle.value = false
    return
  }
  emit('update-column', { id: props.column.id, title: newTitle.value.trim() })
  editingTitle.value = false
}

// Local copy of tasks for draggable reactivity
const localTasks = ref([...props.column.tasks])

watch(() => props.column.tasks, (t) => { localTasks.value = [...t] }, { deep: true })

function onDragEnd(evt) {
  const taskId = localTasks.value[evt.newIndex]?.id
  if (!taskId) return
  emit('task-moved', {
    task_id: taskId,
    column_id: props.column.id,
    order: evt.newIndex,
  })
}
</script>
