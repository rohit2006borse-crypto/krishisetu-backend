import api from '../api/axios'

export async function createRazorpayOrder(order_id: number, amount: number){
  const res = await api.post('/api/payments/create-order', { order_id, amount })
  return res.data
}

export async function verifyRazorpay(razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string){
  const res = await api.post('/api/payments/verify', { razorpay_order_id, razorpay_payment_id, razorpay_signature })
  return res.data
}
