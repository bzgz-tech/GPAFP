<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">配置系统运行所需的关键参数</p>
      </div>
    </div>

    <div class="settings-content">
      <el-card shadow="hover" class="setting-card">
        <template #header>
          <div class="card-header">
            <span>AI 模型配置</span>
            <el-tag type="success" v-if="aiConfigured" effect="plain" size="small">已配置</el-tag>
            <el-tag type="warning" v-else effect="plain" size="small">未配置</el-tag>
          </div>
        </template>
        
        <el-form :model="aiForm" ref="aiFormRef" :rules="aiRules" label-width="120px" status-icon>
          <el-form-item label="AI 提供商" prop="ai_provider">
            <el-select v-model="aiForm.ai_provider" placeholder="选择提供商" @change="handleProviderChange">
              <el-option 
                v-for="item in providers" 
                :key="item.value" 
                :label="item.label" 
                :value="item.value" 
              />
            </el-select>
            <div class="form-tip" v-if="currentProviderTip">{{ currentProviderTip }}</div>
          </el-form-item>

          <el-form-item label="Base URL" prop="ai_base_url">
            <el-input v-model="aiForm.ai_base_url" placeholder="例如: https://api.deepseek.com/v1" />
            <div class="form-tip">API 请求的基础地址</div>
          </el-form-item>

          <el-form-item label="模型名称" prop="ai_model">
            <el-input v-model="aiForm.ai_model" placeholder="例如: deepseek-chat" />
          </el-form-item>

          <el-form-item label="API Key" prop="ai_api_key">
            <el-input v-model="aiForm.ai_api_key" type="password" show-password placeholder="输入 API Key" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveAiConfig" :loading="saving">保存配置</el-button>
            <el-button @click="testConnection" :loading="testing">测试连接</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

const saving = ref(false)
const testing = ref(false)
const aiConfigured = ref(false)
const aiFormRef = ref()

const aiForm = reactive({
  ai_provider: '',
  ai_base_url: '',
  ai_chat_path: 'chat/completions',
  ai_model: '',
  ai_api_key: ''
})

const aiRules = {
  ai_provider: [{ required: true, message: '请选择 AI 提供商', trigger: 'change' }],
  ai_base_url: [{ required: true, message: '请输入 Base URL', trigger: 'blur' }],
  ai_chat_path: [{ required: true, message: '请输入 Chat Path', trigger: 'blur' }],
  ai_model: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  ai_api_key: [{ required: true, message: '请输入 API Key', trigger: 'blur' }]
}

// Provider definitions
const providers = [
  { 
    label: 'DeepSeek', 
    value: 'deepseek', 
    config: { base_url: 'https://api.deepseek.com/v1', model: 'deepseek-chat', chat_path: 'chat/completions' },
    tip: 'DeepSeek API Key 通常以 sk- 开头'
  },
  { 
    label: 'Aliyun DashScope (Qwen)', 
    value: 'aliyun', 
    config: { base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus', chat_path: 'chat/completions' },
    tip: '请使用阿里云百炼平台的 API Key'
  },
  { 
    label: 'Zhipu AI (GLM)', 
    value: 'zhipu', 
    config: { base_url: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4', chat_path: 'chat/completions' },
    tip: '智谱 AI Key 通常包含一个点号分隔符'
  },
  { 
    label: 'Kimi (Moonshot)', 
    value: 'kimi', 
    config: { base_url: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-8k', chat_path: 'chat/completions' },
    tip: 'Moonshot AI 兼容 OpenAI 格式'
  },
  { 
    label: 'Yi (01.AI)', 
    value: 'yi', 
    config: { base_url: 'https://api.lingyiwanwu.com/v1', model: 'yi-large', chat_path: 'chat/completions' },
    tip: '零一万物 API Key 以 sk- 开头'
  },
  { 
    label: 'Volcengine (Doubao)', 
    value: 'volcengine', 
    config: { base_url: 'https://ark.cn-beijing.volces.com/api/v3', model: '', chat_path: 'chat/completions' },
    tip: '注意：模型名称请填写 Endpoint ID (如 ep-2024...) 而非模型名'
  },
  { 
    label: 'OpenAI', 
    value: 'openai', 
    config: { base_url: 'https://api.openai.com/v1', model: 'gpt-4o', chat_path: 'chat/completions' },
    tip: '请确保网络环境可以访问 OpenAI API'
  },
  { 
    label: 'Custom (OpenAI Compatible)', 
    value: 'custom', 
    config: { base_url: '', model: '', chat_path: 'chat/completions' },
    tip: '适用于任何兼容 OpenAI 接口规范的服务'
  }
]

const currentProviderTip = computed(() => {
  const p = providers.find(item => item.value === aiForm.ai_provider)
  return p ? p.tip : ''
})

const handleProviderChange = (val: string) => {
  const provider = providers.find(p => p.value === val)
  if (provider && provider.value !== 'custom') {
    // Only auto-fill if the fields are empty or match another provider's default
    // To be safe and simple: we confirm with user or just overwrite if it looks like a default?
    // Current strategy: Always overwrite Base URL and Chat Path. Overwrite Model if it's empty or looks like a default.
    // Actually, for better UX, let's just overwrite them. User picked a provider, they expect defaults.
    aiForm.ai_base_url = provider.config.base_url
    if (provider.config.model) aiForm.ai_model = provider.config.model
    aiForm.ai_chat_path = provider.config.chat_path
  }
}


const loadSettings = async () => {
  try {
    // Load all settings
    const { data } = await api.get('/settings/')
    if (data && Array.isArray(data)) {
      data.forEach((item: any) => {
        if (item.key in aiForm) {
          // @ts-ignore
          aiForm[item.key] = item.value
        }
      })
    }
    
    // Check status
    const { data: status } = await api.get('/settings/config/ai_status')
    aiConfigured.value = status.configured
  } catch (e) {
    console.error('Failed to load settings', e)
    ElMessage.error('加载设置失败')
  }
}

const saveAiConfig = async () => {
  if (!aiFormRef.value) return
  
  await aiFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      saving.value = true
      try {
        // Save each field
        for (const [key, value] of Object.entries(aiForm)) {
          await api.post('/settings/', { key, value })
        }
        ElMessage.success('配置已保存')
        aiConfigured.value = true
      } catch (e) {
        console.error('Failed to save settings', e)
        ElMessage.error('保存设置失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const testConnection = async () => {
  if (!aiFormRef.value) return
  
  // Validate basic fields before testing (at least API key and Base URL)
  await aiFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      testing.value = true
      try {
        const { data } = await api.post('/settings/config/test_connection', aiForm)
        if (data.success) {
            ElMessage.success('连接测试成功')
        } else {
            ElMessage.error('连接测试失败: ' + data.message)
        }
      } catch (e: any) {
        console.error('Test connection failed', e)
        const msg = e.response?.data?.detail || e.message || '连接测试请求失败'
        ElMessage.error(msg)
      } finally {
        testing.value = false
      }
    }
  })
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setting-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
  margin-top: 4px;
}
</style>
