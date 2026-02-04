'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { isAuthenticated, clearAuthTokens } from '@/lib/auth'

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (!isAuthenticated()) {
      router.push('/admin/login')
    }
  }, [router])

  const handleLogout = () => {
    clearAuthTokens()
    router.push('/admin/login')
  }

  if (!mounted) {
    return null
  }

  const navItems = [
    { name: 'Dashboard', href: '/admin/dashboard' },
    { name: 'Edit Profile', href: '/admin/edit-profile' },
    { name: 'Edit Projects', href: '/admin/edit-projects' },
    { name: 'Edit Experience', href: '/admin/edit-experience' },
    { name: 'Manage Blogs', href: '/admin/manage-blogs' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-primary-600">Admin Panel</h1>
        </div>
        <nav className="p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`block px-4 py-2 rounded-lg transition-colors ${
                    pathname === item.href
                      ? 'bg-primary-100 text-primary-700 font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {item.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        {children}
      </main>
    </div>
  )
}
