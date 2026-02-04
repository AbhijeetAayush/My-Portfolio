'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { blogsAPI } from '@/lib/api'
import BlogCard from '@/components/BlogCard'

export default function BlogPage() {
  const [blogs, setBlogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchBlogs()
  }, [])

  const fetchBlogs = async () => {
    try {
      setLoading(true)
      const response = await blogsAPI.getAll({ limit: 50 })
      setBlogs(response.data.data.items || [])
      setError(null)
    } catch (err: any) {
      console.error('Error fetching blogs:', err)
      setError('Failed to load blogs. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-primary-500 to-primary-700 text-white">
        <div className="container mx-auto px-6 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl font-bold mb-6"
          >
            Blog
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-white/90 max-w-2xl mx-auto"
          >
            Thoughts, insights, and stories from my journey
          </motion.p>
        </div>
      </section>

      {/* Blog Posts */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          {loading ? (
            <div className="text-center text-gray-600 py-20">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p className="mt-4">Loading blogs...</p>
            </div>
          ) : error ? (
            <div className="text-center text-red-600 py-20">
              <p>{error}</p>
              <button
                onClick={fetchBlogs}
                className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Retry
              </button>
            </div>
          ) : blogs.length === 0 ? (
            <div className="text-center text-gray-600 py-20">
              <p className="text-xl">No blog posts yet. Check back soon!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {blogs.map((blog, index) => (
                <BlogCard key={blog.blogId} blog={blog} index={index} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
