<template>
  <div class="section-container" v-if="report">
    <el-card shadow="hover" class="report-card">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon><Document /></el-icon>
            AI 深度分析报告
          </span>
          <div class="header-actions" v-if="model">
             <span class="model-label">当前模型:</span>
             <el-tag effect="plain" type="primary" size="small">{{ model }}</el-tag>
          </div>
        </div>
      </template>
      <div class="markdown-body" v-html="renderedReport"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import { Document } from '@element-plus/icons-vue'

const props = defineProps<{
  report: string
  model: string
}>()

const renderedReport = computed(() => {
  if (!props.report) return ''
  return marked.parse(props.report)
})
</script>

<style scoped>
.section-container {
  margin-bottom: 48px;
}

.report-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-label {
  font-size: 13px;
  color: #909399;
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 15px;
  line-height: 1.7;
  color: #24292e;
  padding: 8px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin-top: 1.2em;
  margin-bottom: 0.6em;
  font-weight: 600;
  line-height: 1.25;
  color: #1f2d3d;
}

.markdown-body :deep(h3) {
  font-size: 1.1em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
  margin-top: 1.5em;
}

.markdown-body :deep(h4) {
  font-size: 1em;
  margin-top: 1em;
}

.markdown-body :deep(p) {
  margin-bottom: 1em;
  text-align: justify;
}

.markdown-body :deep(ul), 
.markdown-body :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.markdown-body :deep(li) {
  margin-bottom: 0.4em;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #303133;
  background: rgba(64, 158, 255, 0.1);
  padding: 0 2px;
  border-radius: 2px;
}

.markdown-body :deep(blockquote) {
  margin: 1em 0;
  padding: 0.5em 1em;
  color: #606266;
  background-color: #f5f7fa;
  border-left: 4px solid #409eff;
  border-radius: 2px;
}
</style>
