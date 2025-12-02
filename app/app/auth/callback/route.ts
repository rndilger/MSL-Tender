import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin

  console.log('Auth callback - code:', code ? 'present' : 'missing')

  if (code) {
    const supabase = await createClient()
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (error) {
      console.error('Auth callback error:', error)
      return NextResponse.redirect(`${origin}/admin/login?error=${error.message}`)
    }
    
    console.log('Auth callback - session established for:', data.user?.email)
  }

  // Redirect to dashboard after successful authentication
  return NextResponse.redirect(`${origin}/admin/dashboard`)
}
