import React, { useEffect, useState } from 'react'
import { listProducts } from '../services/products'
import { Link } from 'react-router-dom'

export default function Home(){
  const [products, setProducts] = useState<any[]>([])
  useEffect(() => { load() }, [])
  async function load(){
    try{
      const data = await listProducts()
      setProducts(data)
    }catch(err){ console.error(err) }
  }
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Products</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map(p => (
          <div key={p.id} className="bg-white p-4 rounded shadow">
            <h2 className="font-semibold">{p.name}</h2>
            <p className="text-sm text-gray-500">{p.category}</p>
            <p className="mt-2">₹{p.price}</p>
            <Link to={`/products/${p.id}`} className="text-blue-600 mt-2 inline-block">View</Link>
          </div>
        ))}
      </div>
    </div>
  )
}
