import React, { useEffect, useState } from 'react'
import { getProduct } from '../services/products'
import { useParams } from 'react-router-dom'

export default function ProductDetail(){
  const { id } = useParams()
  const [product, setProduct] = useState<any|null>(null)
  useEffect(()=>{ if(id) load() },[id])
  async function load(){
    try{
      const res = await getProduct(Number(id))
      setProduct(res)
    }catch(err){ console.error(err) }
  }
  if(!product) return <div>Loading...</div>
  return (
    <div className="bg-white p-6 rounded shadow max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold">{product.name}</h1>
      <p className="text-sm text-gray-500">{product.category}</p>
      <p className="mt-4">{product.description}</p>
      <p className="mt-4 font-semibold">₹{product.price}</p>
    </div>
  )
}
