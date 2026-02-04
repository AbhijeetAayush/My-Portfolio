'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import { format } from 'date-fns'

interface BlogCardProps {
  blog: {
    blogId: string
    title: string
    slug: string
    featured_image_url?: string
    seo_description?: string
    published_at: number
    reading_time?: number
    likes_count?: number
    comments_count?: number
    tags?: string[]
  }
  index: number
}

export default function BlogCard({ blog, index }: BlogCardProps) {
  const formatDate = (timestamp: number) => {
    try {
      return format(new Date(timestamp * 1000), 'MMM d, yyyy')
    } catch {
      return 'Recent'
    }
  }

  return (
    <motion.article
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
    >
      {blog.featured_image_url && (
        <Link href={`/blog/${blog.slug}`}>
          <div className="relative h-64 w-full overflow-hidden">
            <Image
              src={blog.featured_image_url}
              alt={blog.title}
              fill
              className="object-cover hover:scale-110 transition-transform duration-300"
            />
          </div>
        </Link>
      )}
      <div className="p-6">
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
          <span>{formatDate(blog.published_at)}</span>
          {blog.reading_time && (
            <>
              <span>•</span>
              <span>{blog.reading_time} min read</span>
            </>
          )}
        </div>
        <Link href={`/blog/${blog.slug}`}>
          <h2 className="text-2xl font-bold mb-3 text-gray-900 hover:text-primary-600 transition-colors">
            {blog.title}
          </h2>
        </Link>
        {blog.seo_description && (
          <p className="text-gray-600 mb-4 line-clamp-3">{blog.seo_description}</p>
        )}
        {blog.tags && blog.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {blog.tags.slice(0, 3).map((tag, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        <div className="flex items-center gap-6 text-sm text-gray-500">
          {blog.likes_count !== undefined && (
            <span>❤️ {blog.likes_count} likes</span>
          )}
          {blog.comments_count !== undefined && (
            <span>💬 {blog.comments_count} comments</span>
          )}
        </div>
      </div>
    </motion.article>
  )
}
