<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <span class="modal-title">{{ editTask ? 'Edit Task' : 'New Task' }}</span>
        <button class="btn btn-icon btn-ghost" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <div class="field">
          <label>Title *</label>
          <input v-model="form.title" placeholder="What needs to be done?" autofocus />
        </div>

        <div class="field">
          <label>Description</label>
          <textarea v-model="form.description" placeholder="Add more details…" rows="3" />
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="field">
            <label>Priority</label>
            <select v-model="form.priority">
              <option value="low">🟢 Low</option>
              <option value="medium">🟡 Medium</option>
              <option value="high">🔴 High</option>
              <option value="urgent">🚨 Urgent</option>
            </select>
          </div>

          <div class="field">
            <label>Label</label>
            <select v-model="form.label">
              <option value="">None</option>
              <option value="feature">Feature</option>
              <option value="bug">Bug</option>
              <option value="improvement">Improvement</option>
              <option value="design">Design</option>
              <option value="docs">Docs</option>
              <option value="research">Research</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label>Due Date</label>
          <input type="date" v-model="form.due_date" />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary" :disabled="!form.title.trim() || saving" @click="submit">
          <span v-if="saving" class="spinner" style="width:14px;height:14px;border-width:2px"></span>
          {{ editTask ? 'Save Changes' : 'Create Task' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  columnId: String,
  editTask: { type: Object, default: null },
})
const emit = defineEmits(['close', 'created', 'updated'])

const saving = ref(false)
const form = ref({
  title: '',
  description: '',
  priority: 'medium',
  label: '',
  due_date: '',
})

watch(() => props.editTask, (t) => {
  if (t) {
    form.value = {
      title: t.title,
      description: t.description || '',
      priority: t.priority || 'medium',
      label: t.label || '',
      due_date: t.due_date || '',
    }
  }
}, { immediate: true })

async function submit() {
  if (!form.value.title.trim()) return
  saving.value = true
  const payload = {
    ...form.value,
    due_date: form.value.due_date || null,
    label: form.value.label || '',
  }
  if (props.editTask) {
    emit('updated', { id: props.editTask.id, ...payload })
  } else {
    emit('created', { column: props.columnId, ...payload })
  }
  saving.value = false
}
</script>
