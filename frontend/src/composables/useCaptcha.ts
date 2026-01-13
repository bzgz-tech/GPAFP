import { ref } from 'vue'
import api from '@/services/api'

export function useCaptcha() {
  const captchaId = ref('')
  const captchaUrl = ref('')
  const captchaCode = ref('')

  const fetchCaptcha = async () => {
    try {
      const res = await api.get('/auth/captcha')
      captchaId.value = res.data.captcha_id
      captchaUrl.value = res.data.image
      captchaCode.value = '' // Reset code on refresh
    } catch (error) {
      console.error('Failed to fetch captcha', error)
    }
  }

  return {
    captchaId,
    captchaUrl,
    captchaCode,
    fetchCaptcha
  }
}
