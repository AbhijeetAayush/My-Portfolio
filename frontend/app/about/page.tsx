'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'
import Image from 'next/image'

export default function AboutPage() {
  const [portfolio, setPortfolio] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    portfolioAPI
      .get()
      .then((res) => {
        setPortfolio(res.data.data)
      })
      .catch((err) => {
        console.error('Error fetching portfolio:', err)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-primary-500 to-primary-700 text-white">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto text-center"
          >
            {portfolio?.profile_pic_url && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="mb-8"
              >
                <Image
                  src={portfolio.profile_pic_url}
                  alt="Profile"
                  width={200}
                  height={200}
                  className="rounded-full mx-auto border-4 border-white shadow-lg"
                />
              </motion.div>
            )}
            <h1 className="text-5xl font-bold mb-6">About Me</h1>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <p className="text-xl text-white/90 max-w-2xl mx-auto">
                {portfolio?.bio || 'Creative professional passionate about building amazing experiences.'}
              </p>
            )}
          </motion.div>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto">
            {loading ? (
              <div className="text-center text-gray-600">Loading...</div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="prose prose-lg max-w-none"
              >
                <div
                  dangerouslySetInnerHTML={{
                    __html: portfolio?.about_content || '<p>Content coming soon...</p>',
                  }}
                />
              </motion.div>
            )}
          </div>
        </div>
      </section>

      {/* Social Links */}
      {portfolio?.social_links && Object.keys(portfolio.social_links).length > 0 && (
        <section className="py-20 bg-gray-50">
          <div className="container mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center"
            >
              <h2 className="text-3xl font-bold mb-8 text-gray-900">Connect With Me</h2>
              <div className="flex justify-center gap-6">
                {Object.entries(portfolio.social_links).map(([platform, url]: [string, any]) => (
                  <a
                    key={platform}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-2xl text-primary-600 hover:text-primary-700 transition-colors"
                  >
                    {platform}
                  </a>
                ))}
              </div>
            </motion.div>
          </div>
        </section>
      )}
    </div>
  )
}
