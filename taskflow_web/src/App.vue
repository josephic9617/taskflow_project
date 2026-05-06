<template>
  <div id="app">
    <!-- Sidebar -->
    <aside class="sidebar slide-in-left">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-container">
          <svg viewBox="0 0 24 24" class="logo-svg">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="currentColor" class="logo-path" />
          </svg>
        </div>
        <span class="logo-text">TaskFlow</span>
      </div>

      <!-- Boards section -->
      <div class="sidebar-section-title">Workspaces</div>
        <VueDraggable
          v-model="boards"
          :group="{ name: 'boards', pull: true, put: false }"
          class="sidebar-nav"
        >
          <div
            v-for="b in boards"
            :key="b.id"
            class="sidebar-item"
            :class="{ active: activeBoard?.id === b.id, selected: isSelected('board', b.id) }"
            @click="selectBoard(b.id)"
          >
            <input type="checkbox" :checked="isSelected('board', b.id)" @click.stop="toggleSelect('board', b.id)" class="item-checkbox" />
            <span class="sidebar-board-color" :style="{ background: b.color }" />
            <span class="truncate flex-1">{{ b.title }}</span>
            <span class="item-badge">{{ b.task_count }}</span>
            <div class="sidebar-item-actions">
              <button class="btn-icon btn-sm" @click.stop="openEditBoard(b)" title="Edit board">✏️</button>
              <button class="btn-icon btn-sm" @click.stop="deleteBoard(b.id)" title="Delete board">✕</button>
            </div>
          </div>
        </VueDraggable>

        <div
          class="sidebar-item"
          style="margin-top:8px;border:1px dashed var(--border);color:var(--text-muted)"
          @click="openCreateBoard"
        >
          <span class="item-icon">＋</span>
          New Board
        </div>
      <!-- Bottom links -->
      <div style="padding:12px 10px;border-top:1px solid var(--border)">
        <div class="sidebar-item" @click="openAdminPanel">
          <span class="item-icon">⚙️</span> Admin Panel
        </div>
        <div class="sidebar-item" @click="openApiDocs">
          <span class="item-icon">📡</span> API Docs
        </div>
      </div>

      <!-- Trash Zone (Multi-Group) -->
      <div class="sidebar-trash-container">
        <div class="flex items-center justify-between mb-2 px-1" v-if="selectedItems.length">
          <span class="text-xs font-bold text-red">{{ selectedItems.length }} Selected</span>
          <button class="btn btn-ghost btn-xs" @click="selectedItems = []">Clear</button>
        </div>
        <VueDraggable
          v-model="trashItems"
          :group="{ name: 'trash', pull: false, put: ['tasks', 'columns', 'boards'] }"
          class="sidebar-trash"
          @add="onItemTrashed"
        >
          <div class="trash-inner">
            <span class="trash-icon">🗑️</span>
            <span class="trash-text">{{ selectedItems.length > 0 ? 'Drop to delete selected' : 'Drop to delete' }}</span>
          </div>
        </VueDraggable>
      </div>
    </aside>

    <!-- Main -->
    <div class="main-content">
      <!-- Topbar -->
      <header class="topbar">
        <span class="topbar-title">
          {{ activeBoard ? activeBoard.title : 'Select a Board' }}
        </span>

        <!-- WS status badge -->
        <div class="topbar-ws-badge">
          <span class="ws-dot" :class="{ connected: wsConnected }" />
          {{ wsConnected ? 'Live' : 'Offline' }}
        </div>

        <!-- Seed button -->
        <button
          v-if="activeBoard && !activeBoard.columns?.length && !loadingBoard"
          class="btn btn-primary btn-sm"
          @click="seedBoard"
          :disabled="seeding"
        >
          <span v-if="seeding" class="spinner" style="width:12px;height:12px;border-width:2px" />
          🚀 Load Sample Data
        </button>

        <!-- Refresh -->
        <button class="btn btn-ghost btn-sm" @click="refreshBoard" :disabled="loadingBoard" v-if="activeBoard">
          🔄
        </button>
      </header>

      <!-- Board View -->
      <BoardView
        v-if="activeBoard"
        :board="activeBoard"
        :loading="loadingBoard"
        :selectedItems="selectedItems"
        @refresh="refreshBoard"
        @toggle-select="toggleSelect($event.type, $event.id)"
        @ws-status="wsConnected = $event"
      />

      <!-- No board selected -->
      <div v-else class="no-board fade-in">
        <div style="font-size:56px">📋</div>
        <div style="font-size:18px;font-weight:700;color:var(--text-primary)">Welcome to TaskFlow</div>
        <div style="font-size:13px;color:var(--text-secondary);text-align:center;max-width:300px;line-height:1.7">
          Select a board from the sidebar or create a new one to get started.
        </div>
        <button class="btn btn-primary" @click="openCreateBoard">
          ＋ Create Your First Board
        </button>
      </div>
    </div>

    <!-- Board Modal -->
    <BoardModal
      v-if="boardModal.open"
      :editBoard="boardModal.board"
      @close="boardModal.open = false"
      @created="onBoardCreated"
      @updated="onBoardUpdated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import BoardView from './components/BoardView.vue'
import BoardModal from './components/BoardModal.vue'
import { boardsApi, columnsApi, tasksApi } from './services/api.js'

const boards = ref([])
const activeBoard = ref(null)
const loadingBoard = ref(false)
const boardModal = ref({ open: false, board: null })
const wsConnected = ref(false)
const seeding = ref(false)
const selectedItems = ref([])
const trashItems = ref([])

function isSelected(type, id) {
  return selectedItems.value.some(item => item.type === type && item.id === id)
}

function toggleSelect(type, id) {
  const idx = selectedItems.value.findIndex(item => item.type === type && item.id === id)
  if (idx > -1) selectedItems.value.splice(idx, 1)
  else selectedItems.value.push({ type, id })
}

async function loadBoards() {
  const res = await boardsApi.list()
  boards.value = res.data
}

function openCreateBoard() {
  boardModal.value = { open: true, board: null }
}

function openEditBoard(board) {
  boardModal.value = { open: true, board }
}

async function selectBoard(id) {
  loadingBoard.value = true
  activeBoard.value = null
  try {
    const res = await boardsApi.get(id)
    activeBoard.value = res.data
  } finally {
    loadingBoard.value = false
  }
}

async function refreshBoard() {
  if (!activeBoard.value) return
  loadingBoard.value = true
  try {
    const res = await boardsApi.get(activeBoard.value.id)
    activeBoard.value = res.data
    await loadBoards()
  } finally {
    loadingBoard.value = false
  }
}

async function seedBoard() {
  if (!activeBoard.value) return
  seeding.value = true
  try {
    const res = await boardsApi.seed(activeBoard.value.id)
    activeBoard.value = res.data
    await loadBoards()
  } finally {
    seeding.value = false
  }
}

async function onBoardCreated(data) {
  const res = await boardsApi.create(data)
  boardModal.value.open = false
  await loadBoards()
  selectBoard(res.data.id)
}

async function onBoardUpdated(payload) {
  const { id, ...data } = payload
  await boardsApi.update(id, data)
  boardModal.value.open = false
  await loadBoards()
  if (activeBoard.value?.id === id) refreshBoard()
}

async function onItemTrashed(evt) {
  let itemsToDelete = [...selectedItems.value]
  
  // If nothing selected, detect the item from the drop event
  if (itemsToDelete.length === 0) {
    const item = trashItems.value[0]
    if (item) {
      let type = ''
      if ('task_count' in item) type = 'board'
      else if ('tasks' in item) type = 'column'
      else if ('priority' in item) type = 'task'
      
      if (type) itemsToDelete.push({ type, id: item.id, title: item.title })
    }
  }

  if (itemsToDelete.length > 0) {
    const names = itemsToDelete.map(i => i.title || i.type).join(', ')
    if (confirm(`Delete these ${itemsToDelete.length} items? (${names})`)) {
      for (const item of itemsToDelete) {
        try {
          if (item.type === 'board') await boardsApi.delete(item.id)
          else if (item.type === 'column') await columnsApi.delete(item.id)
          else if (item.type === 'task') await tasksApi.delete(item.id)
        } catch (e) { console.error(`Failed to delete ${item.type}`, e) }
      }
      selectedItems.value = []
      await loadBoards()
      if (activeBoard.value) refreshBoard()
    }
  }
  trashItems.value = []
}

async function deleteBoard(id) {
  if (!confirm('Are you sure you want to delete this board and all its tasks?')) return
  await boardsApi.delete(id)
  if (activeBoard.value?.id === id) activeBoard.value = null
  await loadBoards()
}

function openAdminPanel() {
  window.open('http://localhost:8000/admin/', '_blank')
}
function openApiDocs() {
  window.open('http://localhost:8000/api/', '_blank')
}

onMounted(async () => {
  await loadBoards()
  if (boards.value.length) selectBoard(boards.value[0].id)
})
</script>
