'use client'

import { useState, useEffect } from 'react'
import { likesAPI } from '@/lib/api'

interface BlogLikesProps {
  blogId: string
  initialLikes: number
}

export default function BlogLikes({ blogId, initialLikes }: BlogLikesProps) {
  const [likesCount, setLikesCount] = useState(initialLikes)
  const [hasLiked, setHasLiked] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchLikes()
  }, [blogId])

  const fetchLikes = async () => {
    try {
      const response = await likesAPI.get(blogId)
      setLikesCount(response.data.data.likes_count)
      setHasLiked(response.data.data.has_liked || false)
    } catch (err) {
      console.error('Error fetching likes:', err)
    }
  }

  const handleLike = async () => {
    if (hasLiked || loading) return

    try {
      setLoading(true)
      const response = await likesAPI.add(blogId)
      setLikesCount(response.data.data.likes_count)
      setHasLiked(true)
    } catch (err) {
      console.error('Error adding like:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleLike}
      disabled={hasLiked || loading}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        hasLiked
          ? 'bg-red-100 text-red-600 cursor-not-allowed'
          : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-600'
      }`}
    >
      <span className="text-xl">{hasLiked ? '❤️' : '🤍'}</span>
      <span className="font-semibold">{likesCount}</span>
      <span>{hasLiked ? 'Liked' : 'Like'}</span>
    </button>
  )
}
