<template>
  <div class="board-view" :style="{ '--board-color': board?.color }">
    <!-- Toolbar -->
    <div class="board-toolbar">
      <div class="flex-col gap-1">
        <h1 style="font-size:16px;font-weight:700;color:var(--text-primary)">
          {{ board?.title }}
        </h1>
        <span v-if="board?.description" style="font-size:12px;color:var(--text-secondary)">
          {{ board.description }}
        </span>
        <div class="flex items-center gap-3" style="margin-top:4px">
          <span style="font-size:11px; color:var(--text-muted); font-weight:600">
            📊 {{ totalTasks }} Tasks
          </span>
          <span style="font-size:11px; color:var(--green); font-weight:600">
            ✅ {{ doneTasks }} Done
          </span>
        </div>
      </div>
      
      <div style="flex:1" />

      <!-- Search & Filters -->
      <div class="flex items-center gap-3">
        <div class="field" style="margin:0; min-width:180px">
          <input v-model="searchQuery" placeholder="🔍 Search tasks..." style="padding: 6px 12px; font-size:12px" />
        </div>
        <select v-model="priorityFilter" style="padding: 6px 10px; font-size:12px; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); color:var(--text-secondary); outline:none">
          <option value="all">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
        <button class="btn btn-ghost btn-sm" @click="showAddColumnInput = true" v-if="!showAddColumnInput">
          + Add Column
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" style="width:36px;height:36px;border-width:3px" />
      <span style="color:var(--text-secondary)">Loading board…</span>
    </div>

    <!-- Board columns -->
    <div v-else class="board-columns">
      <VueDraggable
        v-model="board.columns"
        :group="{ name: 'columns', pull: true, put: false }"
        style="display:flex;gap:16px;align-items:flex-start"
        @end="onColumnDragEnd"
      >
        <ColumnCard
          v-for="col in filteredColumns"
          :key="col.id"
          :column="col"
          :allColumns="board.columns"
          :selectedItems="selectedItems"
          @toggle-select="$emit('toggle-select', $event)"
          @add-task="openAddTask"
          @edit-task="openEditTask"
          @delete-task="deleteTask"
          @delete-column="deleteColumn"
          @task-moved="onTaskMoved"
          @update-column="updateColumn"
        />
      </VueDraggable>

      <!-- Add column -->
      <div v-if="showAddColumnInput" style="width:260px;min-width:260px">
        <div class="column-card" style="height:auto;padding:14px">
          <div class="field" style="margin-bottom:10px">
            <input
              v-model="newColumnTitle"
              placeholder="Column name"
              @keyup.enter="addColumn"
              @keyup.escape="showAddColumnInput=false"
              autofocus
              ref="colInput"
            />
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-primary btn-sm" @click="addColumn" :disabled="!newColumnTitle.trim()">Add</button>
            <button class="btn btn-ghost btn-sm" @click="showAddColumnInput=false">Cancel</button>
          </div>
        </div>
      </div>
      <div v-else class="add-column-card" @click="showAddColumnInput = true">
        + Add Column
      </div>
    </div>

    <!-- Task Modal -->
    <TaskModal
      v-if="taskModal.open"
      :columnId="taskModal.columnId"
      :editTask="taskModal.task"
      @close="taskModal.open = false"
      @created="onTaskCreated"
      @updated="onTaskUpdated"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted, computed } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import ColumnCard from './ColumnCard.vue'
import TaskModal from './TaskModal.vue'
import { columnsApi, tasksApi } from '../services/api.js'
import { BoardWebSocket } from '../services/websocket.js'

const props = defineProps({ board: Object, loading: Boolean, selectedItems: Array })
const emit = defineEmits(['refresh', 'ws-status', 'toggle-select'])

// --- Filter & Search ---
const searchQuery = ref('')
const priorityFilter = ref('all')

const filteredColumns = computed(() => {
  if (!props.board?.columns) return []
  return props.board.columns.map(col => {
    return {
      ...col,
      tasks: col.tasks.filter(task => {
        const matchesSearch = task.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            (task.description || '').toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesPriority = priorityFilter.value === 'all' || task.priority === priorityFilter.value
        return matchesSearch && matchesPriority
      })
    }
  })
})

const totalTasks = computed(() => {
  return props.board?.columns?.reduce((acc, col) => acc + col.tasks.length, 0) || 0
})

const doneTasks = computed(() => {
  return props.board?.columns?.find(col => col.title.toLowerCase() === 'done')?.tasks?.length || 0
})

// --- Add Column ---
const showAddColumnInput = ref(false)
const newColumnTitle = ref('')
const colInput = ref(null)

watch(showAddColumnInput, async (v) => {
  if (v) { await nextTick(); colInput.value?.focus() }
})

async function addColumn() {
  if (!newColumnTitle.value.trim()) return
  const maxOrder = props.board.columns.length
  await columnsApi.create({
    board: props.board.id,
    title: newColumnTitle.value.trim(),
    order: maxOrder,
  })
  newColumnTitle.value = ''
  showAddColumnInput.value = false
  emit('refresh')
}

async function deleteColumn(colId) {
  if (!confirm('Delete this column and all its tasks?')) return
  await columnsApi.delete(colId)
  emit('refresh')
}

async function updateColumn(payload) {
  const { id, ...data } = payload
  await columnsApi.update(id, data)
  emit('refresh')
}

// --- Task Modal ---
const taskModal = ref({ open: false, columnId: null, task: null })

function openAddTask(columnId) {
  taskModal.value = { open: true, columnId, task: null }
}
function openEditTask(task) {
  taskModal.value = { open: true, columnId: task.column, task }
}

async function onTaskCreated(payload) {
  await tasksApi.create(payload)
  taskModal.value.open = false
  emit('refresh')
}

async function onTaskUpdated(payload) {
  const { id, ...data } = payload
  await tasksApi.update(id, data)
  taskModal.value.open = false
  emit('refresh')
}

async function deleteTask(taskId) {
  await tasksApi.delete(taskId)
  emit('refresh')
}

// --- Drag & Drop ---
async function onColumnDragEnd(evt) {
  // We'll implement column re-ordering if needed, but for now just to allow dragging out
  // The trash handles the deletion if dropped there.
}

async function onTaskMoved(payload) {
  await tasksApi.move(payload)
  // Board will update via WebSocket broadcast OR re-fetch
  emit('refresh')
}

// --- WebSocket ---
let ws = null

watch(() => props.board?.id, (id) => {
  ws?.disconnect()
  ws = null
  if (!id) return
  ws = new BoardWebSocket(id, {
    onConnected: () => emit('ws-status', true),
    onDisconnected: () => emit('ws-status', false),
    onTaskMoved: () => emit('refresh'),
    onTaskCreated: () => emit('refresh'),
    onTaskUpdated: () => emit('refresh'),
    onTaskDeleted: () => emit('refresh'),
  })
}, { immediate: true })

onUnmounted(() => ws?.disconnect())
</script>
