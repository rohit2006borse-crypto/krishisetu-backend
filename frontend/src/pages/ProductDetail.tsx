import React, { useEffect, useState } from 'react'
import { getProduct } from '../services/products'
import { useParams } from 'react-router-dom'
import { addCartItem } from '../services/cart'

export default function ProductDetail(){
  const { id } = useParams()
  const [product, setProduct] = useState<any|null>(null)
  const [qty, setQty] = useState<number>(1)
  useEffect(()=>{ if(id) load() },[id])
  async function load(){
    try{
      const res = await getProduct(Number(id))
      setProduct(res)
    }catch(err){ console.error(err) }
  }
  async function add(){
    try{
      await addCartItem(product.id, qty)
      alert('Added to cart')
    }catch(err){
      console.error(err)
      alert('Failed to add to cart')
    }
  }
  if(!product) return <div>Loading...</div>
  return (
    <div className="bg-white p-6 rounded shadow max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold">{product.name}</h1>
      <p className="text-sm text-gray-500">{product.category}</p>
      <p className="mt-4">{product.description}</p>
      <p className="mt-4 font-semibold">₹{product.price}</p>

      <div className="mt-4 flex items-center space-x-2">
        <label>Quantity</label>
        <input type="number" min={1} value={qty} onChange={e=>setQty(Number(e.target.value))} className="w-20 border p-1" />
        <button onClick={add} className="bg-green-600 text-white px-4 py-2 rounded">Add to cart</button>
      </div>
    </div>
  )
}
