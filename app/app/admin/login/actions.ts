'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

export async function login(formData: FormData) {
  const email = formData.get('email') as string
  const password = formData.get('password') as string

  // Validate @illinois.edu domain
  if (!email.endsWith('@illinois.edu')) {
    return { error: 'Please use your @illinois.edu email address' }
  }

  if (!password) {
    return { error: 'Please enter your password' }
  }

  const supabase = await createClient()

  // Sign in with password
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) {
    console.error('[Server Login] Error:', error)
    return { error: 'Invalid email or password' }
  }

  console.log('[Server Login] Success! User:', data.user?.email)

  // Check admin_users table
  const { data: adminUser, error: adminError } = await supabase
    .from('admin_users')
    .select('*')
    .eq('id', data.user.id)
    .single()

  if (!adminUser) {
    console.error('[Server Login] User not in admin whitelist')
    return { error: 'User authenticated but not in admin whitelist. Please contact administrator.' }
  }

  console.log('[Server Login] All checks passed, redirecting to dashboard')

  // Revalidate the cache for the dashboard
  revalidatePath('/admin/dashboard')
  
  // Redirect to dashboard
  redirect('/admin/dashboard')
}
