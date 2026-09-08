import api from '../api/axios'

export async function addCartItem(product_id: number, quantity: number){
  const res = await api.post('/api/cart/items', { product_id, quantity })
  return res.data
}

export async function getCart(){
  const res = await api.get('/api/cart')
  return res.data
}

export async function updateCartItem(item_id: number, quantity: number){
  const res = await api.put(`/api/cart/items/${item_id}`, { product_id: 0, quantity })
  return res.data
}

export async function clearCart(){
  const res = await api.delete('/api/cart/clear')
  return res.data
}
