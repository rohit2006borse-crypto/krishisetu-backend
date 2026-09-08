import React, { useEffect, useState } from 'react'
import { getCart, clearCart } from '../services/cart'
import { createOrder } from '../services/orders'
import { createRazorpayOrder, verifyRazorpay } from '../services/payments'

export default function Cart(){
  const [cart, setCart] = useState<any>({ items: [], total_amount: 0 })
  const [loading, setLoading] = useState(false)

  useEffect(()=>{ load() },[])
  async function load(){
    try{
      const data = await getCart()
      setCart(data)
    }catch(err){ console.error(err) }
  }

  async function checkout(){
    if(cart.items.length === 0){ alert('Cart is empty'); return }
    setLoading(true)
    try{
      // Prepare order items for backend
      const items = cart.items.map((it:any) => ({ product_id: it.product_id, quantity: it.quantity }))
      const order = await createOrder(items)
      // Create razorpay order (server-side)
      const paymentResp = await createRazorpayOrder(order.id, Number(order.total_amount))
      const razorOrder = paymentResp.razorpay_order
      // Load Razorpay checkout
      const options: any = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || '',
        amount: razorOrder.amount, // in paise
        currency: razorOrder.currency,
        name: 'Krishisetu',
        description: `Order #${order.id}`,
        order_id: razorOrder.id,
        handler: async function (response: any){
          try{
            await verifyRazorpay(response.razorpay_order_id, response.razorpay_payment_id, response.razorpay_signature)
            alert('Payment successful and verified')
            await clearCart()
            load()
          }catch(err){
            console.error(err)
            alert('Payment verification failed')
          }
        },
        prefill: {
          name: '',
          email: ''
        },
        modal: {
          ondismiss: function(){ console.log('Checkout closed') }
        }
      }
      // Dynamically load Razorpay script
      const script = document.createElement('script')
      script.src = 'https://checkout.razorpay.com/v1/checkout.js'
      script.onload = () => {
        // @ts-ignore
        const rzp = new window.Razorpay(options)
        rzp.open()
      }
      document.body.appendChild(script)

    }catch(err){
      console.error(err)
      alert('Checkout failed')
    }finally{ setLoading(false) }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-xl font-bold mb-4">Cart</h1>
      {cart.items.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <div>
          <ul>
            {cart.items.map((it:any) => (
              <li key={it.id} className="flex justify-between py-2 border-b">
                <div>
                  <div className="font-semibold">{it.product.name}</div>
                  <div className="text-sm text-gray-500">Qty: {it.quantity}</div>
                </div>
                <div>₹{Number(it.product.price) * it.quantity}</div>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex justify-between items-center">
            <div className="font-bold">Total: ₹{cart.total_amount}</div>
            <div>
              <button onClick={checkout} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded">{loading ? 'Processing...' : 'Checkout'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
