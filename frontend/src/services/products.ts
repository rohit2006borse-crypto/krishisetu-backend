import api from '../api/axios'

export async function listProducts(params = {}){
  const res = await api.get('/api/products', { params })
  return res.data
}

export async function getProduct(id: number){
  const res = await api.get(`/api/products/${id}`)
  return res.data
}
