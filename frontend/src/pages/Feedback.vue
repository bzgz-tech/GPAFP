<template>
  <div class="feedback-container">
    <div class="page-header">
      <h2>
        <el-icon style="vertical-align: middle; margin-right: 8px"><ChatDotRound /></el-icon>
        意见反馈与社区
      </h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Edit /></el-icon> 我要反馈
      </el-button>
    </div>

    <el-card class="feedback-list-card">
        <el-table :data="allFeedbacks" style="width: 100%" v-loading="loading" @row-click="handleRowClick" class="clickable-rows">
           <el-table-column prop="title" label="主题" min-width="200">
             <template #default="scope">
                <span class="feedback-title">{{ scope.row.title }}</span>
                <el-tag size="small" :type="scope.row.feedback_type === 'bug' ? 'danger' : 'success'" style="margin-left: 10px">
                    {{ scope.row.feedback_type === 'bug' ? '缺陷' : '改进' }}
                </el-tag>
                <el-icon v-if="scope.row.attachments && scope.row.attachments.length" style="margin-left: 5px; vertical-align: middle"><Paperclip /></el-icon>
             </template>
           </el-table-column>
           <el-table-column prop="username" label="作者" width="120"></el-table-column>
           <el-table-column prop="created_at" label="发布时间" width="160">
             <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
           </el-table-column>
           <el-table-column prop="updated_at" label="最新更新" width="160">
             <template #default="scope">{{ formatDate(scope.row.updated_at) }}</template>
           </el-table-column>
           <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
           </el-table-column>
           <el-table-column prop="comment_count" label="回复数" width="80" align="center"></el-table-column>
        </el-table>
        <div class="pagination-container" style="margin-top: 15px; display: flex; justify-content: flex-end;">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
        </div>
    </el-card>

    <!-- Create Feedback Dialog -->
    <el-dialog v-model="showCreateDialog" title="提交新反馈" width="700px">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
            <el-form-item label="标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入简短标题"></el-input>
            </el-form-item>
            <el-form-item label="类型" prop="feedback_type">
              <el-radio-group v-model="form.feedback_type">
                <el-radio label="bug">缺陷报告</el-radio>
                <el-radio label="improvement">功能改进</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="详细描述" prop="content">
                <div @paste="handlePaste($event, 'create')">
                    <QuillEditor 
                        ref="quillCreateRef"
                        v-model:content="form.content" 
                        contentType="html"
                        :options="createEditorOptions"
                        style="height: 300px"
                        @focus="currentUploadContext = 'create'"
                    />
                </div>
            </el-form-item>
            <el-form-item label="附件">
                <el-upload
                    action="#"
                    :http-request="(opts) => uploadAttachment(opts, 'create')"
                    :on-remove="(file) => removeAttachment(file, 'create')"
                    :file-list="createFileList"
                    multiple
                >
                    <el-button size="small" type="primary">点击上传附件</el-button>
                    <template #tip>
                        <div class="el-upload__tip">
                            支持 jpg/png/pdf/doc 等文件，单个不超过 10MB
                        </div>
                    </template>
                </el-upload>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
              <el-button @click="showCreateDialog = false">
                <el-icon><Close /></el-icon> 取消
              </el-button>
              <el-button type="primary" @click="submitFeedback" :loading="submitting">
                <el-icon><Check /></el-icon> 提交
              </el-button>
            </span>
        </template>
    </el-dialog>

    <!-- Detail / Thread Dialog -->
    <el-dialog v-model="showDetailDialog" :title="currentFeedback?.title || '加载中...'" width="900px" custom-class="feedback-detail-dialog" destroy-on-close>
        <div class="thread-container" v-loading="loadingDetail" style="min-height: 300px">
            <div v-if="currentFeedback">
                <!-- Main Post -->
                <div class="main-post">
                <div class="post-header">
                    <span class="author">{{ currentFeedback.username }}</span>
                    <span class="time">{{ formatDate(currentFeedback.created_at) }}</span>
                    <el-tag size="small" :type="currentFeedback.feedback_type === 'bug' ? 'danger' : 'success'">
                        {{ currentFeedback.feedback_type === 'bug' ? '缺陷' : '改进' }}
                    </el-tag>
                    <el-tag size="small" :type="getStatusType(currentFeedback.status)" style="margin-left: 5px">
                        {{ getStatusText(currentFeedback.status) }}
                    </el-tag>
                </div>
                <!-- Render Content with Markdown -->
                <div class="post-content markdown-body" v-html="renderMarkdown(currentFeedback.content)" @click="handleContentClick"></div>
                
                <!-- Attachments Display -->
                <div v-if="currentFeedback.attachments && currentFeedback.attachments.length" class="attachments-list">
                    <div class="attachment-label">附件:</div>
                    <div v-for="(file, idx) in currentFeedback.attachments" :key="idx" class="attachment-item">
                        <el-link :href="file.url" target="_blank" type="primary">
                            <el-icon><Paperclip /></el-icon> {{ file.name }}
                        </el-link>
                    </div>
                </div>

                <!-- Admin Official Reply / Status Note -->
                <div v-if="currentFeedback.reply" class="official-reply">
                    <div class="reply-label">管理员回复/状态说明:</div>
                    <div class="reply-content" v-html="renderMarkdown(currentFeedback.reply)"></div>
                </div>

                <!-- Admin Actions -->
                <div v-if="isAdmin" class="admin-actions">
                    <el-divider content-position="left">管理操作</el-divider>
                    <el-form size="small" label-position="top">
                        <el-form-item label="状态">
                            <el-select v-model="adminForm.status" style="width: 150px">
                                <el-option label="待处理" value="pending"></el-option>
                                <el-option label="已采纳" value="adopted"></el-option>
                                <el-option label="已解决" value="resolved"></el-option>
                                <el-option label="已关闭" value="closed"></el-option>
                            </el-select>
                        </el-form-item>
                        <el-form-item label="官方说明">
                            <el-input 
                                type="textarea" 
                                v-model="adminForm.reply" 
                                :rows="3"
                                placeholder="请输入状态变更说明或官方回复..."
                            ></el-input>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="updateFeedbackStatus">更新状态</el-button>
                        </el-form-item>
                    </el-form>
                </div>
            </div>

            <el-divider>评论 ({{ currentFeedback.comments?.length || 0 }})</el-divider>

            <!-- Comments List -->
            <div class="comments-list">
                <div v-for="(comment, index) in currentFeedback.comments" :key="comment.id" class="comment-item">
                    <div class="comment-header">
                        <span class="comment-floor">#{{ index + 1 }}</span>
                        <span class="comment-author">{{ comment.username }}</span>
                        <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <div class="comment-content markdown-body" v-html="renderMarkdown(comment.content)" @click="handleContentClick"></div>
                    <!-- Comment Attachments -->
                    <div v-if="comment.attachments && comment.attachments.length" class="attachments-list small">
                        <div v-for="(file, idx) in comment.attachments" :key="idx" class="attachment-item">
                            <el-link :href="file.url" target="_blank" type="primary" :underline="false">
                                <el-icon><Paperclip /></el-icon> {{ file.name }}
                            </el-link>
                        </div>
                    </div>
                </div>
                <div v-if="!currentFeedback.comments || currentFeedback.comments.length === 0" class="no-comments">
                    暂无评论
                </div>
            </div>

            <!-- Add Comment -->
            <div class="add-comment-section">
                <div @paste="handlePaste($event, 'comment')">
                    <QuillEditor 
                        ref="quillCommentRef"
                        v-model:content="newComment" 
                        contentType="html"
                        :options="commentEditorOptions"
                        style="height: 200px"
                        @focus="currentUploadContext = 'comment'"
                    />
                </div>
                
                <div class="comment-attachments" style="margin-top: 60px">
                    <el-upload
                        action="#"
                        :http-request="(opts) => uploadAttachment(opts, 'comment')"
                        :on-remove="(file) => removeAttachment(file, 'comment')"
                        :file-list="commentFileList"
                        multiple
                        class="upload-inline"
                    >
                        <el-button size="small">
                             <el-icon><Paperclip /></el-icon> 添加附件
                        </el-button>
                    </el-upload>
                </div>

                <div class="comment-actions">
                    <el-button type="primary" size="small" @click="submitComment" :loading="submittingComment" :disabled="!newComment.trim()">发表评论</el-button>
                </div>
            </div>
            </div>
        </div>
    </el-dialog>
    
    <!-- Hidden File Input for Image Insertion -->
    <input type="file" ref="imageInputRef" style="display: none" accept="image/*" @change="handleImageFileChange" />

    <!-- Image Viewer -->
    <el-image-viewer
        v-if="showImageViewer"
        :url-list="previewImageList"
        @close="showImageViewer = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/store'
import api from '@/services/api'
import { ElMessage, ElImageViewer } from 'element-plus'
import dayjs from 'dayjs'
import { marked } from 'marked'
import { Picture, Paperclip, Plus, Check, Close, Edit, ChatDotRound } from '@element-plus/icons-vue'

import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const store = useUserStore()
const isAdmin = computed(() => store.user?.username === 'admin')

// Data
const allFeedbacks = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// Create Form
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  title: '',
  feedback_type: 'bug',
  content: '',
  attachments: [] as any[]
})
const createFileList = ref<any[]>([])

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// Detail View
const showDetailDialog = ref(false)
const currentFeedback = ref<any>(null)
const loadingDetail = ref(false)
const newComment = ref('')
const submittingComment = ref(false)
const commentFileList = ref<any[]>([])
const newCommentAttachments = ref<any[]>([])

// Admin Form
const adminForm = reactive({
    status: '',
    reply: ''
})

// Image Upload Helper
const imageInputRef = ref()
const currentUploadContext = ref('') // 'create' or 'comment'
const quillCreateRef = ref()
const quillCommentRef = ref()

// Image Viewer State
const showImageViewer = ref(false)
const previewImageList = ref<string[]>([])

const handleContentClick = (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (target.tagName === 'IMG') {
        const src = (target as HTMLImageElement).src
        if (src) {
            previewImageList.value = [src]
            showImageViewer.value = true
        }
    }
}

const imageHandler = (context: string) => {
    currentUploadContext.value = context
    imageInputRef.value.click()
}

const getEditorOptions = (context: string) => ({
    theme: 'snow',
    modules: {
        toolbar: {
            container: [
                ['bold', 'italic', 'underline', 'strike'],
                ['blockquote', 'code-block'],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                [{ 'color': [] }, { 'background': [] }],
                ['link', 'image'],
                ['clean']
            ],
            handlers: {
                image: () => imageHandler(context)
            }
        }
    },
    placeholder: '请输入内容...'
})

const createEditorOptions = getEditorOptions('create')
const commentEditorOptions = getEditorOptions('comment')

const formatDate = (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm')

const getStatusText = (status: string) => {
  const map: any = { pending: '待处理', adopted: '已采纳', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
}
const getStatusType = (status: string) => {
  const map: any = { pending: 'info', adopted: 'primary', resolved: 'success', closed: 'warning' }
  return map[status] || 'info'
}

const renderMarkdown = (content: string) => {
    if (!content) return ''
    return marked.parse(content)
}

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/feedback/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    allFeedbacks.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchFeedbacks()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchFeedbacks()
}

const openCreateDialog = () => {
    showCreateDialog.value = true
    resetForm()
}

// File Upload Logic
const uploadFile = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data // { name, url, type }
}

const uploadAttachment = async (options: any, context: string) => {
    try {
        const res = await uploadFile(options.file)
        const attachment = { name: res.name, url: res.url }
        if (context === 'create') {
            form.attachments.push(attachment)
            // element-plus file-list needs specific format, but we handle state manually too?
            // Actually options.onSuccess handles UI list if we use default behavior,
            // but we are using custom http-request.
            // We should update the fileList ref bound to el-upload
            // Since we bound file-list, we just need to ensure consistency?
            // Element Plus updates file-list automatically for added files, but we need to link our response.
        } else {
            newCommentAttachments.value.push(attachment)
        }
        options.onSuccess(res)
    } catch (error) {
        options.onError(error)
        ElMessage.error('上传失败')
    }
}

const removeAttachment = (file: any, context: string) => {
    // file is the element-plus file object
    // We need to remove from our attachments array
    if (context === 'create') {
        const idx = form.attachments.findIndex(a => a.name === file.name)
        if (idx > -1) form.attachments.splice(idx, 1)
    } else {
        const idx = newCommentAttachments.value.findIndex(a => a.name === file.name)
        if (idx > -1) newCommentAttachments.value.splice(idx, 1)
    }
}

// Image Insert Logic
const triggerImageUpload = (context: string) => {
    currentUploadContext.value = context
    imageInputRef.value.click()
}

const handleImageFileChange = async (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    try {
        const res = await uploadFile(file)
        insertImageToContent(res.url, res.name, currentUploadContext.value)
    } catch (error) {
        ElMessage.error('图片上传失败')
    }
    e.target.value = '' // Reset
}

const handlePaste = async (event: ClipboardEvent, context: string) => {
    const items = event.clipboardData?.items
    if (!items) return

    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const file = items[i].getAsFile()
            if (file) {
                event.preventDefault() // Prevent default paste if it's image
                try {
                    const res = await uploadFile(file)
                    insertImageToContent(res.url, res.name || 'image.png', context)
                } catch (error) {
                    ElMessage.error('粘贴图片上传失败')
                }
            }
        }
    }
}

const insertImageToContent = (url: string, name: string, context: string) => {
    let quill
    if (context === 'create') {
        quill = quillCreateRef.value.getQuill()
    } else {
        quill = quillCommentRef.value.getQuill()
    }
    if (quill) {
        const range = quill.getSelection(true)
        if (range) {
             quill.insertEmbed(range.index, 'image', url)
             quill.setSelection(range.index + 1)
        } else {
             // If lost focus, insert at end? or current position
             const length = quill.getLength()
             quill.insertEmbed(length, 'image', url)
        }
    }
}

const submitFeedback = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        await api.post('/feedback/', form)
        ElMessage.success('提交成功')
        showCreateDialog.value = false
        resetForm()
        fetchFeedbacks()
      } catch (error) {
        ElMessage.error('提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  form.title = ''
  form.content = ''
  form.feedback_type = 'bug'
  form.attachments = []
  createFileList.value = []
}

const handleRowClick = async (row: any) => {
    showDetailDialog.value = true
    loadingDetail.value = true
    currentFeedback.value = null // Reset first
    newComment.value = ''
    commentFileList.value = []
    newCommentAttachments.value = []
    
    try {
        const { data } = await api.get(`/feedback/${row.id}`)
        currentFeedback.value = data
        // Init admin form
        adminForm.status = data.status
        adminForm.reply = data.reply || ''
    } catch (error) {
        ElMessage.error('获取详情失败')
        showDetailDialog.value = false
    } finally {
        loadingDetail.value = false
    }
}

const submitComment = async () => {
    if (!newComment.value.trim() || !currentFeedback.value) return
    submittingComment.value = true
    try {
        await api.post(`/feedback/${currentFeedback.value.id}/comments`, {
            content: newComment.value,
            attachments: newCommentAttachments.value
        })
        ElMessage.success('评论成功')
        newComment.value = ''
        newCommentAttachments.value = []
        commentFileList.value = []
        
        // Refresh detail
        const { data } = await api.get(`/feedback/${currentFeedback.value.id}`)
        currentFeedback.value = data
        // Also refresh list to update count
        fetchFeedbacks()
    } catch (error) {
        ElMessage.error('评论失败')
    } finally {
        submittingComment.value = false
    }
}

const updateFeedbackStatus = async () => {
    if (!currentFeedback.value) return
    try {
        await api.put(`/feedback/${currentFeedback.value.id}`, {
            status: adminForm.status,
            reply: adminForm.reply
        })
        ElMessage.success('状态更新成功')
        // Refresh detail
        const { data } = await api.get(`/feedback/${currentFeedback.value.id}`)
        currentFeedback.value = data
        // Also refresh list
        fetchFeedbacks()
    } catch (error) {
        ElMessage.error('更新失败')
    }
}

onMounted(() => {
  fetchFeedbacks()
})
</script>

<style scoped>
.feedback-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.feedback-list-card {
    border-radius: 8px;
}
.feedback-title {
    font-weight: 600;
    color: var(--color-text-primary);
}
.clickable-rows {
    cursor: pointer;
}

/* Detail View Styles */
.thread-container {
    padding: 10px;
}
.main-post {
    margin-bottom: 20px;
}
.post-header {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.author {
    font-weight: bold;
    font-size: 16px;
}
.time {
    color: #909399;
    font-size: 14px;
}
.post-content {
    font-size: 15px;
    line-height: 1.6;
    color: var(--color-text-primary);
    background: var(--color-bg-overlay);
    padding: 15px;
    border-radius: 8px;
}
.official-reply {
    margin-top: 15px;
    padding: 10px;
    background: rgba(64, 158, 255, 0.1);
    border-left: 4px solid var(--color-primary);
    border-radius: 4px;
}
.reply-label {
    font-weight: bold;
    color: var(--color-primary);
    margin-bottom: 5px;
}
.admin-actions {
    margin-top: 20px;
    padding-top: 10px;
}

.comments-list {
    margin-top: 20px;
}
.comment-item {
    padding: 15px 0;
    border-bottom: 1px solid var(--border-color-base);
}
.comment-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 13px;
}
.comment-floor {
    color: #909399;
}
.comment-author {
    font-weight: bold;
}
.comment-time {
    color: #909399;
}
.comment-content {
    font-size: 14px;
    line-height: 1.5;
}
.no-comments {
    text-align: center;
    color: #909399;
    padding: 20px;
}
.add-comment-section {
    margin-top: 20px;
    border-top: 1px solid var(--border-color-base);
    padding-top: 20px;
}
.comment-actions {
    margin-top: 10px;
    text-align: right;
}

.editor-toolbar {
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.tip {
    font-size: 12px;
    color: #909399;
}
.attachments-list {
    margin-top: 10px;
}
.attachment-label {
    font-weight: bold;
    font-size: 13px;
    margin-bottom: 5px;
}
.attachment-item {
    margin-bottom: 2px;
}
.attachments-list.small {
    margin-top: 5px;
    padding-left: 10px;
    border-left: 2px solid #eee;
}
.comment-attachments {
    margin-top: 10px;
}
/* Markdown/HTML Content Styles */
.markdown-body :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 10px 0;
    display: block; /* Ensure it doesn't sit on baseline if that's an issue */
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); /* Add a subtle shadow */
    cursor: zoom-in; /* Indicate clickable */
}
.markdown-body :deep(p) {
    margin-bottom: 8px;
    line-height: 1.6;
}
.markdown-body :deep(ul), .markdown-body :deep(ol) {
    padding-left: 20px;
    margin-bottom: 8px;
}
.markdown-body :deep(blockquote) {
    border-left: 4px solid #ccc;
    margin: 0;
    padding-left: 10px;
    color: #666;
}
.markdown-body :deep(pre) {
    background-color: #f6f8fa;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
}
</style>
