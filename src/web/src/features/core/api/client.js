import axios from 'axios'

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '/api/v1').trim()
const cleanBaseUrl = rawBaseUrl.replace(/\/+$/, '')
// Garante o prefixo /api/v1 caso tenha sido informado apenas a raiz do domínio (ex: https://vigitel-ap.onrender.com)
const baseURL = (cleanBaseUrl.startsWith('http://') || cleanBaseUrl.startsWith('https://')) && !cleanBaseUrl.endsWith('/api/v1')
  ? `${cleanBaseUrl}/api/v1`
  : cleanBaseUrl

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 15000, // Timeout estendido para acomodar eventuais cold starts em nuvens gratuitas
  paramsSerializer: {
    indexes: null // Previne o uso de brackets (foo[]=1) e envia no formato FastAPI (foo=1&foo=2)
  }
})

// Interceptor para logs
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Não loga no console se a requisição foi abortada intencionalmente para dar lugar a um novo filtro
    if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED') {
      return Promise.reject(error)
    }
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
