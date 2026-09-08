import React, { useState } from 'react'
import { login } from '../services/auth'
import { useNavigate } from 'react-router-dom'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  async function submit(e: any){
    e.preventDefault()
    try{
      const res = await login(email, password)
      localStorage.setItem('access_token', res.access_token)
      navigate('/')
    }catch(err){
      alert('Login failed')
    }
  }
  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-xl font-bold mb-4">Login</h1>
      <form onSubmit={submit}>
        <label className="block">Email</label>
        <input value={email} onChange={e => setEmail(e.target.value)} className="w-full border p-2 mb-2" />
        <label className="block">Password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full border p-2 mb-4" />
        <button className="bg-blue-600 text-white px-4 py-2 rounded">Login</button>
      </form>
    </div>
  )
}
