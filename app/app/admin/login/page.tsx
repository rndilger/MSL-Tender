'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

export const dynamic = 'force-dynamic'

export default function AdminLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const router = useRouter()

  useEffect(() => {
    const hash = window.location.hash
    if (hash.includes('error=')) {
      const params = new URLSearchParams(hash.substring(1))
      const error = params.get('error')
      const errorDescription = params.get('error_description')
      console.error('Auth error from URL:', error, errorDescription)
      setMessage(`Authentication error: ${errorDescription || error}`)
      window.history.replaceState(null, '', window.location.pathname)
    }
  }, [])

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const supabase = createClient()

    // Validate @illinois.edu domain
    if (!email.endsWith('@illinois.edu')) {
      setMessage('Please use your @illinois.edu email address')
      setLoading(false)
      return
    }

    if (!password) {
      setMessage('Please enter your password')
      setLoading(false)
      return
    }

    try {
      console.log('[Password Login] Attempting login for:', email)

      // Sign in with password
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        console.error('[Password Login] Error:', error)
        setMessage('Invalid email or password')
        setLoading(false)
        return
      }

      console.log('[Password Login] Success! User:', data.user?.email)
      console.log('[Password Login] Session:', data.session ? 'Present' : 'Missing')
      
      // Check admin_users table
      const { data: adminUser, error: adminError } = await supabase
        .from('admin_users')
        .select('*')
        .eq('id', data.user.id)
        .single()
      
      console.log('[Password Login] Admin user check:', adminUser ? 'Found' : 'Not found', adminError)
      
      if (!adminUser) {
        setMessage('User authenticated but not in admin whitelist. Please contact administrator.')
        setLoading(false)
        return
      }

      console.log('[Password Login] All checks passed, redirecting to dashboard...')
      
      // Use Next.js router to navigate
      router.push('/admin/dashboard')
      router.refresh()
    } catch (error) {
      setMessage('An unexpected error occurred. Please try again.')
      console.error('Login error:', error)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            MSL-Tender Admin
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in with your @illinois.edu email
          </p>
        </div>
        
        <form onSubmit={handleLogin} className="mt-8 space-y-6">
          <div>
            <label htmlFor="email" className="sr-only">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="your.email@illinois.edu"
            />
          </div>

          <div>
            <label htmlFor="password" className="sr-only">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>

          {message && (
            <div
              className={`text-sm p-3 rounded ${
                message.includes('error') || message.includes('Invalid')
                  ? 'bg-red-50 text-red-800 border border-red-200'
                  : 'bg-green-50 text-green-800 border border-green-200'
              }`}
            >
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            Password-based authentication for @illinois.edu accounts
          </p>
        </div>
      </div>
    </div>
  )
}
