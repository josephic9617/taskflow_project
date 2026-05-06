<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <span class="modal-title">{{ editBoard ? 'Edit Board' : 'New Board' }}</span>
        <button class="btn btn-icon btn-ghost" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="field">
          <label>Board Name *</label>
          <input v-model="form.title" placeholder="e.g. Product Roadmap" autofocus />
        </div>
        <div class="field">
          <label>Description</label>
          <textarea v-model="form.description" placeholder="What is this board for?" rows="2" />
        </div>
        <div class="field">
          <label>Color</label>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:2px">
            <button
              v-for="c in colors" :key="c"
              @click="form.color = c"
              :style="{
                background: c,
                width: '28px', height: '28px',
                borderRadius: '50%',
                border: form.color === c ? '2px solid white' : '2px solid transparent',
                cursor: 'pointer',
                outline: form.color === c ? '2px solid ' + c : 'none',
                outlineOffset: '2px',
              }"
            />
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary" :disabled="!form.title.trim() || saving" @click="submit">
          <span v-if="saving" class="spinner" style="width:14px;height:14px;border-width:2px"></span>
          {{ editBoard ? 'Save Changes' : 'Create Board' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ editBoard: { type: Object, default: null } })
const emit = defineEmits(['close', 'created', 'updated'])
const saving = ref(false)
const form = ref({ title: '', description: '', color: '#6366f1' })
const colors = ['#6366f1','#8b5cf6','#ec4899','#ef4444','#f59e0b','#10b981','#06b6d4','#3b82f6']

watch(() => props.editBoard, (b) => {
  if (b) {
    form.value = { title: b.title, description: b.description || '', color: b.color || '#6366f1' }
  }
}, { immediate: true })

async function submit() {
  if (!form.value.title.trim()) return
  saving.value = true
  if (props.editBoard) {
    emit('updated', { id: props.editBoard.id, ...form.value })
  } else {
    emit('created', { ...form.value })
  }
  saving.value = false
}
</script>
