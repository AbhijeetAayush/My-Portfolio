'use client'

import { useState, useEffect } from 'react'
import { commentsAPI } from '@/lib/api'
import { format } from 'date-fns'

interface BlogCommentsProps {
  blogId: string
}

interface Comment {
  commentId: string
  author_name: string
  author_email: string
  content: string
  created_at: number
}

export default function BlogComments({ blogId }: BlogCommentsProps) {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    author_name: '',
    author_email: '',
    content: '',
  })

  useEffect(() => {
    fetchComments()
  }, [blogId])

  const fetchComments = async () => {
    try {
      setLoading(true)
      const response = await commentsAPI.getByBlog(blogId)
      setComments(response.data.data || [])
    } catch (err) {
      console.error('Error fetching comments:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.author_name || !formData.author_email || !formData.content) {
      alert('Please fill in all fields')
      return
    }

    try {
      setSubmitting(true)
      await commentsAPI.create(blogId, formData)
      setFormData({ author_name: '', author_email: '', content: '' })
      fetchComments() // Refresh comments
    } catch (err: any) {
      console.error('Error submitting comment:', err)
      alert('Failed to submit comment. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const formatDate = (timestamp: number) => {
    try {
      return format(new Date(timestamp * 1000), 'MMM d, yyyy at h:mm a')
    } catch {
      return 'Recent'
    }
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">
        Comments ({comments.length})
      </h2>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="mb-8 bg-gray-50 p-6 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Your Name"
            value={formData.author_name}
            onChange={(e) => setFormData({ ...formData, author_name: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <input
            type="email"
            placeholder="Your Email"
            value={formData.author_email}
            onChange={(e) => setFormData({ ...formData, author_email: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <textarea
          placeholder="Write your comment..."
          value={formData.content}
          onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 mb-4"
          required
        />
        <button
          type="submit"
          disabled={submitting}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Submitting...' : 'Post Comment'}
        </button>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="text-center text-gray-600 py-8">Loading comments...</div>
      ) : comments.length === 0 ? (
        <div className="text-center text-gray-600 py-8">
          No comments yet. Be the first to comment!
        </div>
      ) : (
        <div className="space-y-6">
          {comments.map((comment) => (
            <div key={comment.commentId} className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-gray-900">{comment.author_name}</h4>
                  <p className="text-sm text-gray-500">{formatDate(comment.created_at)}</p>
                </div>
              </div>
              <p className="text-gray-700 leading-relaxed">{comment.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
