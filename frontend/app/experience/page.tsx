'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'
import { format } from 'date-fns'

export default function ExperiencePage() {
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

  const formatDate = (timestamp: number) => {
    if (!timestamp) return 'Present'
    try {
      return format(new Date(timestamp * 1000), 'MMM yyyy')
    } catch {
      return 'Present'
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
            Experience
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-white/90 max-w-2xl mx-auto"
          >
            My professional journey and achievements
          </motion.p>
        </div>
      </section>

      {/* Experience Timeline */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            {loading ? (
              <div className="text-center text-gray-600">Loading experience...</div>
            ) : (
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-primary-200" />

                {portfolio?.experience?.map((exp: any, index: number) => (
                  <motion.div
                    key={exp.id || index}
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="relative pl-20 pb-12"
                  >
                    {/* Timeline dot */}
                    <div className="absolute left-6 top-2 w-4 h-4 bg-primary-600 rounded-full border-4 border-white shadow-lg" />

                    {/* Content */}
                    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900 mb-1">
                            {exp.title || exp.position}
                          </h3>
                          <p className="text-lg text-primary-600 font-semibold">
                            {exp.company || exp.organization}
                          </p>
                        </div>
                        <div className="text-gray-600 mt-2 md:mt-0">
                          {formatDate(exp.start_date)} - {formatDate(exp.end_date)}
                        </div>
                      </div>
                      {exp.description && (
                        <p className="text-gray-700 leading-relaxed">{exp.description}</p>
                      )}
                      {exp.technologies && exp.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4">
                          {exp.technologies.map((tech: string, i: number) => (
                            <span
                              key={i}
                              className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full"
                            >
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}

                {(!portfolio?.experience || portfolio.experience.length === 0) && (
                  <div className="text-center text-gray-600 py-20">
                    <p className="text-xl">No experience entries yet.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
