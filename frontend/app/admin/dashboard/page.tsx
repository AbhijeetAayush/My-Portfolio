'use client'

import AdminLayout from '@/components/AdminLayout'
import { useEffect, useState } from 'react'
import { portfolioAPI, blogsAPI } from '@/lib/api'
import Link from 'next/link'

export default function AdminDashboardPage() {
  const [stats, setStats] = useState({
    blogs: 0,
    projects: 0,
    experience: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const [portfolioRes, blogsRes] = await Promise.all([
        portfolioAPI.get(),
        blogsAPI.getAll({ limit: 1 }),
      ])
      
      setStats({
        blogs: blogsRes.data.data.items?.length || 0,
        projects: portfolioRes.data.data.projects?.length || 0,
        experience: portfolioRes.data.data.experience?.length || 0,
      })
    } catch (err) {
      console.error('Error fetching stats:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AdminLayout>
      <div>
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Dashboard</h1>

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Blog Posts</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.blogs}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Projects</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.projects}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Experience</h3>
              <p className="text-3xl font-bold text-primary-600">{stats.experience}</p>
            </div>
          </div>
        )}

        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              href="/admin/manage-blogs"
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-semibold mb-2">Create New Blog Post</h3>
              <p className="text-gray-600">Write and publish a new blog post</p>
            </Link>
            <Link
              href="/admin/edit-profile"
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-semibold mb-2">Update Profile</h3>
              <p className="text-gray-600">Edit your profile information</p>
            </Link>
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
