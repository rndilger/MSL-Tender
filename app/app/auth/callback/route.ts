import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin

  console.log('[Auth Callback] Code present:', !!code)

  if (code) {
    // Create response that we'll set cookies on
    const response = NextResponse.redirect(`${origin}/admin/dashboard`)
    
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return request.cookies.getAll()
          },
          setAll(cookiesToSet) {
            console.log('[Auth Callback] Setting cookies:', cookiesToSet.length)
            cookiesToSet.forEach(({ name, value, options }) => {
              console.log('[Auth Callback] Cookie:', name, 'length:', value.length)
              response.cookies.set(name, value, options)
            })
          },
        },
      }
    )

    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (error) {
      console.error('[Auth Callback] Exchange error:', error)
      return NextResponse.redirect(`${origin}/admin/login?error=${error.message}`)
    }

    console.log('[Auth Callback] Session established for:', data.user?.email)
    console.log('[Auth Callback] Response cookies:', response.cookies.getAll().length)
    
    return response
  }

  // No code present, redirect to login
  console.log('[Auth Callback] No code, redirecting to login')
  return NextResponse.redirect(`${origin}/admin/login`)
}
