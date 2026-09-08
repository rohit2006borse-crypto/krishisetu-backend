import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Navbar(){
  const navigate = useNavigate()
  const token = localStorage.getItem('access_token')
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto p-4 flex justify-between items-center">
        <Link to="/" className="font-bold text-xl">Krishisetu</Link>
        <div className="space-x-4">
          <Link to="/">Products</Link>
          <Link to="/cart">Cart</Link>
          <Link to="/bookings">Bookings</Link>
          {token ? (
            <button onClick={() => { localStorage.removeItem('access_token'); navigate('/login')} } className="ml-4">Logout</button>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register" className="ml-2">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
