import axios from 'axios'

const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', timeout: 30000 })
export const api = {
  health: () => client.get('/health'),
  packs: () => client.get('/packs'),
  pack: (id) => client.get(`/packs/${id}`),
  createPack: () => client.post('/packs'),
  upload: (packId, file, documentId, documentType, onUploadProgress) => {
    const data = new FormData()
    data.append('file', file)
    data.append('document_id', documentId)
    data.append('document_type', documentType)
    return client.post(`/packs/${packId}/documents`, data, { onUploadProgress })
  },
  compare: (packId, params) => client.post(`/packs/${packId}/compare`, null, { params }),
}
export const apiError = (error) => error?.response?.data?.detail || error?.message || 'Something went wrong. Please try again.'
