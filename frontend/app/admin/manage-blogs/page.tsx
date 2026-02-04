'use client'

import AdminLayout from '@/components/AdminLayout'
import { useEffect, useState } from 'react'
import { blogsAPI } from '@/lib/api'
import RichTextEditor from '@/components/RichTextEditor'
import Link from 'next/link'

interface Blog {
  blogId: string
  title: string
  slug: string
  content: string
  featured_image_url: string
  tags: string[]
  category: string
  seo_description: string
}

export default function ManageBlogsPage() {
  const [blogs, setBlogs] = useState<Blog[]>([])
  const [loading, setLoading] = useState(true)
  const [editingBlog, setEditingBlog] = useState<Blog | null>(null)
  const [formData, setFormData] = useState<Blog>({
    blogId: '',
    title: '',
    slug: '',
    content: '',
    featured_image_url: '',
    tags: [],
    category: '',
    seo_description: '',
  })
  const [tagInput, setTagInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    fetchBlogs()
  }, [])

  const fetchBlogs = async () => {
    try {
      const response = await blogsAPI.getAll({ limit: 100 })
      setBlogs(response.data.data.items || [])
    } catch (err) {
      console.error('Error fetching blogs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingBlog(null)
    setFormData({
      blogId: '',
      title: '',
      slug: '',
      content: '',
      featured_image_url: '',
      tags: [],
      category: '',
      seo_description: '',
    })
  }

  const handleEdit = (blog: Blog) => {
    setEditingBlog(blog)
    setFormData(blog)
  }

  const handleSave = async () => {
    if (!formData.title || !formData.content) {
      alert('Title and content are required')
      return
    }

    setSaving(true)
    try {
      if (editingBlog) {
        // Update existing blog
        await blogsAPI.update(editingBlog.blogId, formData)
        alert('Blog updated successfully!')
      } else {
        // Create new blog
        await blogsAPI.create(formData)
        alert('Blog created successfully!')
      }
      setEditingBlog(null)
      fetchBlogs()
    } catch (err: any) {
      console.error('Error saving blog:', err)
      alert(err.response?.data?.error || 'Failed to save blog')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (blogId: string) => {
    if (!confirm('Are you sure you want to delete this blog post?')) {
      return
    }

    setDeleting(blogId)
    try {
      await blogsAPI.delete(blogId)
      alert('Blog deleted successfully!')
      fetchBlogs()
      if (editingBlog?.blogId === blogId) {
        setEditingBlog(null)
      }
    } catch (err) {
      console.error('Error deleting blog:', err)
      alert('Failed to delete blog')
    } finally {
      setDeleting(null)
    }
  }

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()],
      })
      setTagInput('')
    }
  }

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }

  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center py-12">Loading...</div>
      </AdminLayout>
    )
  }

  return (
    <AdminLayout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Manage Blogs</h1>
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create New Blog
          </button>
        </div>

        {/* Blog Form */}
        {formData && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-2xl font-bold mb-6">
              {editingBlog ? 'Edit Blog' : 'Create New Blog'}
            </h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => {
                    setFormData({
                      ...formData,
                      title: e.target.value,
                      slug: formData.slug || generateSlug(e.target.value),
                    })
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Blog post title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Slug (URL-friendly)
                </label>
                <input
                  type="text"
                  value={formData.slug}
                  onChange={(e) =>
                    setFormData({ ...formData, slug: e.target.value.toLowerCase() })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                  placeholder="blog-post-slug"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Featured Image URL (Cloudinary)
                </label>
                <input
                  type="url"
                  value={formData.featured_image_url}
                  onChange={(e) =>
                    setFormData({ ...formData, featured_image_url: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="https://res.cloudinary.com/..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., Technology, Design, Personal"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SEO Description
                </label>
                <textarea
                  value={formData.seo_description}
                  onChange={(e) =>
                    setFormData({ ...formData, seo_description: e.target.value })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Brief description for SEO (150-160 characters)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Add a tag and press Enter"
                  />
                  <button
                    type="button"
                    onClick={addTag}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center gap-2"
                    >
                      {tag}
                      <button
                        onClick={() => {
                          setFormData({
                            ...formData,
                            tags: formData.tags.filter((_, idx) => idx !== i),
                          })
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content *
                </label>
                <RichTextEditor
                  value={formData.content}
                  onChange={(value) => setFormData({ ...formData, content: value })}
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : editingBlog ? 'Update Blog' : 'Create Blog'}
                </button>
                {editingBlog && (
                  <button
                    onClick={() => {
                      setEditingBlog(null)
                      setFormData({
                        blogId: '',
                        title: '',
                        slug: '',
                        content: '',
                        featured_image_url: '',
                        tags: [],
                        category: '',
                        seo_description: '',
                      })
                    }}
                    className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Blogs List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">All Blog Posts</h2>
          {blogs.length === 0 ? (
            <div className="text-center py-12 text-gray-600">
              No blog posts yet. Create your first one!
            </div>
          ) : (
            blogs.map((blog) => (
              <div
                key={blog.blogId}
                className="bg-white p-6 rounded-lg shadow flex justify-between items-start"
              >
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{blog.title}</h3>
                  <p className="text-gray-600 text-sm mb-2">
                    Slug: <code className="bg-gray-100 px-2 py-1 rounded">{blog.slug}</code>
                  </p>
                  {blog.category && (
                    <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm mb-2">
                      {blog.category}
                    </span>
                  )}
                  <div className="mt-2">
                    <Link
                      href={`/blog/${blog.slug}`}
                      target="_blank"
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      View Post →
                    </Link>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(blog)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(blog.blogId)}
                    disabled={deleting === blog.blogId}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    {deleting === blog.blogId ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </AdminLayout>
  )
}
