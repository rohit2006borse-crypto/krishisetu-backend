import api from '../api/axios'

export async function login(email: string, password: string){
  const res = await api.post('/api/auth/login', { email, password })
  return res.data
}

export async function register(payload: any){
  const res = await api.post('/api/auth/register', payload)
  return res.data
}

export function logout(){
  localStorage.removeItem('access_token')
}
