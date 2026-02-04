'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { blogsAPI, likesAPI } from '@/lib/api'
import Image from 'next/image'
import { format } from 'date-fns'
import BlogLikes from '@/components/BlogLikes'

export default function BlogPostPage() {
  const params = useParams()
  const slug = params?.slug as string
  const [blog, setBlog] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (slug) {
      fetchBlog()
    }
  }, [slug])

  const fetchBlog = async () => {
    try {
      setLoading(true)
      const response = await blogsAPI.getById(slug)
      setBlog(response.data.data)
      setError(null)
    } catch (err: any) {
      console.error('Error fetching blog:', err)
      setError('Blog post not found')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (timestamp: number) => {
    try {
      return format(new Date(timestamp * 1000), 'MMMM d, yyyy')
    } catch {
      return 'Recent'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading blog post...</p>
        </div>
      </div>
    )
  }

  if (error || !blog) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4 text-gray-900">Blog Not Found</h1>
          <p className="text-gray-600 mb-8">{error || 'The blog post you are looking for does not exist.'}</p>
          <a
            href="/blog"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Back to Blog
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Image */}
      {blog.featured_image_url && (
        <div className="relative h-96 w-full overflow-hidden">
          <Image
            src={blog.featured_image_url}
            alt={blog.title}
            fill
            className="object-cover"
            priority
          />
        </div>
      )}

      {/* Article Content */}
      <article className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
            <span>{formatDate(blog.published_at)}</span>
            {blog.reading_time && (
              <>
                <span>•</span>
                <span>{blog.reading_time} min read</span>
              </>
            )}
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900">
            {blog.title}
          </h1>
          {blog.tags && blog.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {blog.tags.map((tag: string, i: number) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </header>

        {/* Content */}
        <div
          className="prose prose-lg max-w-none mb-12"
          dangerouslySetInnerHTML={{ __html: blog.content }}
        />

        {/* Likes */}
        <div className="border-t border-gray-200 pt-8">
          <div className="flex items-center gap-8">
            <BlogLikes blogId={blog.blogId} initialLikes={blog.likes_count || 0} />
          </div>
        </div>
      </article>
    </div>
  )
}
