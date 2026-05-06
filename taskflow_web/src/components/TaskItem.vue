<template>
  <div class="task-card" :class="{ selected, 'group-dragging': groupDragging }" :data-type="'task'" :data-id="task.id" :data-title="task.title" @contextmenu.prevent="openMenu">
    <div class="task-actions">
      <input type="checkbox" :checked="selected" @click.stop="$emit('toggle-select')" class="item-checkbox" />
      <button draggable="false" class="btn-icon btn-sm" @click.stop="$emit('edit', task)" title="Edit task">✏️</button>
      <button draggable="false" class="btn-icon btn-sm" @click.stop="$emit('delete', task.id)" title="Delete task" style="color:var(--red)">🗑</button>
    </div>
    <div class="task-card-top">
      <div class="task-title">{{ task.title }}</div>
      <button class="task-menu-btn" @click.stop="openMenu">⋯</button>
    </div>

    <div v-if="task.description" style="font-size:12px;color:var(--text-secondary);margin-bottom:6px;line-height:1.5">
      {{ task.description.slice(0, 80) }}{{ task.description.length > 80 ? '…' : '' }}
    </div>

    <div class="task-card-meta">
      <span v-if="task.priority" :class="`badge badge-priority-${task.priority}`">
        {{ priorityIcon[task.priority] }} {{ task.priority }}
      </span>
      <span v-if="task.label" :class="`badge badge-label-${task.label}`">
        {{ task.label }}
      </span>
    </div>

    <div class="task-card-footer" style="display:flex; align-items:center; justify-content:space-between; margin-top:10px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.03)">
      <div style="display:flex; -webkit-mask-image: linear-gradient(to right, black 80%, transparent); mask-image: linear-gradient(to right, black 80%, transparent);">
        <div v-for="i in 1" :key="i" class="avatar" :style="{ background: task.priority === 'urgent' ? 'var(--red)' : 'var(--accent)', width:'22px', height:'22px', borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'10px', fontWeight:'700', border:'2px solid var(--bg-card-hover)' }">
          {{ task.title.charAt(0) }}
        </div>
      </div>
      <span v-if="task.due_date" style="font-size:10px; color:var(--text-muted); display:flex; align-items:center; gap:3px">
        📅 {{ formatDate(task.due_date) }}
      </span>
    </div>

    <!-- Context Menu -->
    <Teleport to="body">
      <div v-if="menuOpen" class="context-menu" :style="menuStyle" @click.stop>
        <div class="context-menu-item" @click="$emit('edit', task); menuOpen=false">
          ✏️ Edit task
        </div>
        <div class="context-menu-item danger" @click="$emit('delete', task.id); menuOpen=false">
          🗑 Delete
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  task: Object,
  selected: Boolean,
  groupDragging: Boolean,
})
const emit = defineEmits(['edit', 'delete', 'toggle-select'])

const menuOpen = ref(false)
const menuStyle = ref({})

const priorityIcon = { low: '🟢', medium: '🟡', high: '🔴', urgent: '🚨' }

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function openMenu(e) {
  menuStyle.value = { top: e.clientY + 'px', left: e.clientX + 'px' }
  menuOpen.value = true
}

function closeMenu() { menuOpen.value = false }

onMounted(() => document.addEventListener('click', closeMenu))
onBeforeUnmount(() => document.removeEventListener('click', closeMenu))
</script>
