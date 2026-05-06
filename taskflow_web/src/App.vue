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
          filter="button, input, .sidebar-item-actions"
          :preventOnFilter="false"
          @start="onBoardDragStart"
          @end="onAnyDragEnd"
        >
          <div
            v-for="b in boards"
            :key="b.id"
            class="sidebar-item"
            :class="{ active: activeBoard?.id === b.id, selected: isSelected('board', b.id), 'group-dragging': isGroupDragging('board', b.id) }"
            :data-type="'board'"
            :data-id="b.id"
            :data-title="b.title"
            @click="selectBoard(b.id)"
          >
            <input type="checkbox" :checked="isSelected('board', b.id)" @click.stop="toggleSelect('board', b.id, { title: b.title })" class="item-checkbox" />
            <span class="sidebar-board-color" :style="{ background: b.color }" />
            <span class="truncate flex-1">{{ b.title }}</span>
            <span class="item-badge">{{ b.task_count }}</span>
            <div class="sidebar-item-actions">
              <button type="button" draggable="false" class="btn-icon btn-sm" @click.stop="openEditBoard(b)" title="Edit board">✏️</button>
              <button type="button" draggable="false" class="btn-icon btn-sm" @click.stop="deleteBoard(b.id)" title="Delete board">✕</button>
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
        <div class="sidebar-trash-actions" v-if="selectedItems.length">
          <span class="sidebar-trash-count">{{ selectedItems.length }} selected</span>
          <div class="flex gap-2">
            <button class="btn btn-ghost btn-sm" @click="clearSelection">Clear</button>
            <button class="btn btn-danger btn-sm" @click="deleteSelectedItems" :disabled="deletingSelected">
              {{ deletingSelected ? 'Deleting...' : 'Delete Selected' }}
            </button>
          </div>
        </div>
        <VueDraggable
          v-model="trashItems"
          :group="{ name: 'trash', pull: false, put: ['tasks', 'columns', 'boards'] }"
          class="sidebar-trash"
          @add="onItemTrashed"
        >
          <div class="trash-inner">
            <span class="trash-icon">🗑️</span>
            <span class="trash-text">{{ trashHint() }}</span>
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

      <div v-if="notice" class="app-banner" :class="`app-banner-${notice.type}`">
        <span>{{ notice.message }}</span>
        <button class="btn-icon btn-sm" @click="clearNotice" title="Dismiss">✕</button>
      </div>

      <!-- Board View -->
      <BoardView
        v-if="activeBoard"
        :board="activeBoard"
        :loading="loadingBoard"
        :selectedItems="selectedItems"
        :groupDragKeys="groupDragKeys"
        @refresh="refreshBoard"
        @toggle-select="toggleSelect($event.type, $event.id, $event.meta)"
        @drag-selection-start="onGroupDragStart"
        @drag-selection-end="onAnyDragEnd"
        @error="showNotice('error', $event)"
        @ws-status="wsConnected = $event"
      />

      <!-- No board selected — full-screen premium welcome -->
      <div v-else class="no-board fade-in">
        <div class="welcome-hero">
          <div class="welcome-logo-ring">
            <div class="welcome-logo-inner">
              <svg viewBox="0 0 24 24" width="44" height="44">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="white" />
              </svg>
            </div>
          </div>
          <h1 class="welcome-title">Welcome to <span class="welcome-accent">TaskFlow</span></h1>
          <p class="welcome-subtitle">
            Your premium workspace for tasks, teams, and projects.<br/>
            Create a board and start organizing.
          </p>
          <div class="welcome-features">
            <div class="welcome-pill">⚡ Real-time sync</div>
            <div class="welcome-pill">🎯 Drag & Drop</div>
            <div class="welcome-pill">🔍 Search & Filter</div>
            <div class="welcome-pill">📊 Progress tracking</div>
          </div>
          <div class="welcome-actions">
            <button class="btn btn-primary welcome-cta" @click="openCreateBoard">
              ＋ Create New Board
            </button>
          </div>
        </div>
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
import { boardsApi, columnsApi, tasksApi, getErrorMessage } from './services/api.js'

const boards = ref([])
const activeBoard = ref(null)
const loadingBoard = ref(false)
const boardModal = ref({ open: false, board: null })
const wsConnected = ref(false)
const seeding = ref(false)
const selectedItems = ref([])
const trashItems = ref([])
const deletingSelected = ref(false)
const notice = ref(null)
const groupDragKeys = ref([])
const groupDragCount = ref(0)

let noticeTimer = null

function isSelected(type, id) {
  return selectedItems.value.some(item => item.type === type && item.id === id)
}

function isGroupDragging(type, id) {
  return groupDragKeys.value.includes(`${type}:${id}`)
}

function itemKey(type, id) {
  return `${type}:${id}`
}

function getGroupDragItems(draggedItem) {
  const draggedItemIsSelected = draggedItem
    ? selectedItems.value.some(item => item.type === draggedItem.type && item.id === draggedItem.id)
    : false

  return draggedItemIsSelected ? selectedItems.value : draggedItem ? [draggedItem] : []
}

function onGroupDragStart(draggedItem) {
  const items = getGroupDragItems(draggedItem)
  groupDragKeys.value = items.map(item => itemKey(item.type, item.id))
  groupDragCount.value = items.length
}

function onBoardDragStart(evt) {
  const board = boards.value[evt.oldIndex]
  if (!board) return
  onGroupDragStart({ type: 'board', id: board.id, title: board.title })
}

function onAnyDragEnd() {
  groupDragKeys.value = []
  groupDragCount.value = 0
}

function trashHint() {
  if (groupDragCount.value > 1) return `Drop to delete ${groupDragCount.value} selected items`
  if (selectedItems.value.length > 0) return 'Drop one selected item or use Delete Selected'
  return 'Drop to delete'
}

function showNotice(type, message) {
  notice.value = { type, message }
  if (noticeTimer) clearTimeout(noticeTimer)
  noticeTimer = setTimeout(() => {
    notice.value = null
    noticeTimer = null
  }, 4000)
}

function clearNotice() {
  notice.value = null
  if (noticeTimer) {
    clearTimeout(noticeTimer)
    noticeTimer = null
  }
}

function clearSelection() {
  selectedItems.value = []
}

function confirmDelete(message) {
  return window.confirm(message)
}

function toggleSelect(type, id, meta = {}) {
  const idx = selectedItems.value.findIndex(item => item.type === type && item.id === id)
  if (idx > -1) selectedItems.value.splice(idx, 1)
  else selectedItems.value.push({ type, id, ...meta })
}

function normalizeItemsForDeletion(items) {
  const unique = new Map(items.map(item => [`${item.type}:${item.id}`, item]))
  const normalized = [...unique.values()]
  const selectedBoardIds = new Set(normalized.filter(item => item.type === 'board').map(item => item.id))
  const selectedColumnIds = new Set(normalized.filter(item => item.type === 'column').map(item => item.id))

  return normalized
    .filter(item => !(item.type === 'column' && item.boardId && selectedBoardIds.has(item.boardId)))
    .filter(item => !(item.type === 'task' && item.columnId && selectedColumnIds.has(item.columnId)))
    .filter(item => !(item.type === 'task' && item.boardId && selectedBoardIds.has(item.boardId)))
    .sort((a, b) => ({ task: 0, column: 1, board: 2 }[a.type] ?? 99) - ({ task: 0, column: 1, board: 2 }[b.type] ?? 99))
}

function inferDraggedItem(item) {
  if (!item) return null
  if ('task_count' in item) return { type: 'board', id: item.id, title: item.title }
  if ('tasks' in item) return { type: 'column', id: item.id, title: item.title, boardId: item.board }
  if ('priority' in item) return { type: 'task', id: item.id, title: item.title, columnId: item.column }
  return null
}

async function deleteItems(items) {
  const failures = []

  for (const item of items) {
    try {
      if (item.type === 'board') await boardsApi.delete(item.id)
      else if (item.type === 'column') await columnsApi.delete(item.id)
      else if (item.type === 'task') await tasksApi.delete(item.id)
    } catch (error) {
      failures.push({ item, message: getErrorMessage(error, `Failed to delete ${item.type}`) })
    }
  }

  return failures
}

async function confirmAndDelete(items) {
  if (!items.length) return

  const names = items.map(item => item.title || item.type).join(', ')
  if (!confirmDelete(`Delete these ${items.length} items? (${names})`)) return

  deletingSelected.value = true
  try {
    const failures = await deleteItems(items)
    if (failures.length) {
      showNotice('error', failures[0].message)
    } else {
      clearSelection()
      showNotice('success', `Deleted ${items.length} item${items.length === 1 ? '' : 's'}.`)
    }
  } finally {
    await syncState()
    deletingSelected.value = false
  }
}

async function loadBoards() {
  const res = await boardsApi.list()
  boards.value = res.data
}

async function syncState() {
  await loadBoards()

  if (!activeBoard.value) return

  const activeBoardStillExists = boards.value.some(board => board.id === activeBoard.value.id)
  if (!activeBoardStillExists) {
    activeBoard.value = null
    return
  }

  const res = await boardsApi.get(activeBoard.value.id)
  activeBoard.value = res.data
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
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to load board'))
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
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to refresh board'))
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
    showNotice('success', 'Sample data loaded.')
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to seed board'))
  } finally {
    seeding.value = false
  }
}

async function onBoardCreated(data) {
  try {
    const res = await boardsApi.create(data)
    boardModal.value.open = false
    await loadBoards()
    selectBoard(res.data.id)
    showNotice('success', 'Board created.')
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to create board'))
  }
}

async function onBoardUpdated(payload) {
  try {
    const { id, ...data } = payload
    await boardsApi.update(id, data)
    boardModal.value.open = false
    await loadBoards()
    if (activeBoard.value?.id === id) refreshBoard()
    showNotice('success', 'Board updated.')
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to update board'))
  }
}

async function onItemTrashed(evt) {
  // Read type/id directly from the dragged DOM element's dataset
  const el = evt.item
  const type = el?.dataset?.type
  const id = el?.dataset?.id
  const title = el?.dataset?.title || type

  let itemsToDelete = []

  if (type && id) {
    const isInSelection = selectedItems.value.some(item => item.type === type && item.id === id)
    if (isInSelection && selectedItems.value.length > 0) {
      // Delete all selected items when any selected item is dragged to trash
      itemsToDelete = normalizeItemsForDeletion([...selectedItems.value])
    } else {
      // Delete just this one item
      itemsToDelete = [{ type, id, title }]
    }
  }

  if (!itemsToDelete.length) {
    trashItems.value = []
    onAnyDragEnd()
    return
  }

  const label = itemsToDelete.length === 1
    ? `"${itemsToDelete[0].title || itemsToDelete[0].type}"`
    : `${itemsToDelete.length} items`

  if (!window.confirm(`Delete ${label}?`)) {
    trashItems.value = []
    onAnyDragEnd()
    await syncState() // restore UI
    return
  }

  deletingSelected.value = true
  try {
    const failures = await deleteItems(itemsToDelete)
    if (failures.length) {
      showNotice('error', failures[0].message)
    } else {
      clearSelection()
      showNotice('success', `Deleted ${label}.`)
    }
  } finally {
    trashItems.value = []
    onAnyDragEnd()
    await syncState()
    deletingSelected.value = false
  }
}

async function deleteSelectedItems() {
  await confirmAndDelete(normalizeItemsForDeletion(selectedItems.value))
}

async function deleteBoard(id) {
  if (!confirmDelete('Are you sure you want to delete this board and all its tasks?')) return
  try {
    await boardsApi.delete(id)
    if (activeBoard.value?.id === id) activeBoard.value = null
    await loadBoards()
    selectedItems.value = selectedItems.value.filter(item => !(item.type === 'board' && item.id === id))
    showNotice('success', 'Board deleted.')
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to delete board'))
  }
}

function openAdminPanel() {
  window.open('http://localhost:8000/admin/', '_blank')
}
function openApiDocs() {
  window.open('http://localhost:8000/api/', '_blank')
}

onMounted(async () => {
  try {
    await loadBoards()
    if (boards.value.length) selectBoard(boards.value[0].id)
  } catch (error) {
    showNotice('error', getErrorMessage(error, 'Failed to load boards'))
  }
})
</script>
