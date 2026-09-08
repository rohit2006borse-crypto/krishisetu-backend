import React, { useState } from 'react'
import { register } from '../services/auth'
import { useNavigate } from 'react-router-dom'

export default function Register(){
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('FARMER')
  const navigate = useNavigate()
  async function submit(e: any){
    e.preventDefault()
    try{
      await register({ name, email, phone, password, role })
      alert('Registered, please login')
      navigate('/login')
    }catch(err){ alert('Registration failed') }
  }
  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-xl font-bold mb-4">Register</h1>
      <form onSubmit={submit}>
        <label className="block">Name</label>
        <input value={name} onChange={e=>setName(e.target.value)} className="w-full border p-2 mb-2" />
        <label className="block">Email</label>
        <input value={email} onChange={e=>setEmail(e.target.value)} className="w-full border p-2 mb-2" />
        <label className="block">Phone</label>
        <input value={phone} onChange={e=>setPhone(e.target.value)} className="w-full border p-2 mb-2" />
        <label className="block">Password</label>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full border p-2 mb-2" />
        <label className="block">Role</label>
        <select value={role} onChange={e=>setRole(e.target.value)} className="w-full border p-2 mb-4">
          <option value="FARMER">FARMER</option>
          <option value="VENDOR">VENDOR</option>
        </select>
        <button className="bg-green-600 text-white px-4 py-2 rounded">Register</button>
      </form>
    </div>
  )
}
