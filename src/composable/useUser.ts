import { ref, onMounted, onUnmounted } from 'vue'

export function useUser() {
  const isLoggedIn = ref(false)
  const cookies = ref<any[]>([])

  const updateLoginState = () => {
    // 简单的逻辑：如果有特定的 cookie（比如 token 或 session），则认为已登录
    // 这里需要根据实际网页的 cookie 名称来调整
    isLoggedIn.value = cookies.value.some(c => 
      c.name.toLowerCase().includes('token') || 
      c.name.toLowerCase().includes('session') ||
      c.name.toLowerCase().includes('uid')
    )
  }

  const handleCookieUpdate = (_event: any, cookie: any) => {
    const index = cookies.value.findIndex(c => c.name === cookie.name)
    if (index > -1) {
      cookies.value[index] = cookie
    } else {
      cookies.value.push(cookie)
    }
    updateLoginState()
  }

  onMounted(() => {
    if (window.ipcRenderer) {
      window.ipcRenderer.on('cookie-updated', handleCookieUpdate)
    }
  })

  onUnmounted(() => {
    if (window.ipcRenderer) {
      window.ipcRenderer.removeAllListeners('cookie-updated')
    }
  })

  return {
    isLoggedIn,
    cookies,
  }
}
