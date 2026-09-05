import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000, // Timeout de 10 segundos para evitar requisições presas
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
