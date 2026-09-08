import api from '../api/axios'

export async function createOrder(items: { product_id: number; quantity: number }[]){
  const res = await api.post('/api/orders', { items })
  return res.data
}

export async function myOrders(){
  const res = await api.get('/api/orders/my')
  return res.data
}
