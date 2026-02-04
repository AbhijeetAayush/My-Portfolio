'use client'

import Hero from '@/components/Hero'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'
import ProjectCard from '@/components/ProjectCard'

export default function Home() {
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
    <div className="min-h-screen">
      <Hero />

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-3xl mx-auto text-center"
          >
            <h2 className="text-4xl font-bold mb-6 text-gray-900">About Me</h2>
            {loading ? (
              <div className="text-gray-600">Loading...</div>
            ) : (
              <p className="text-lg text-gray-700 leading-relaxed">
                {portfolio?.about_content ||
                  'Passionate creative professional dedicated to building beautiful and functional digital experiences.'}
              </p>
            )}
          </motion.div>
        </div>
      </section>

      {/* Projects Section */}
      <section id="projects" className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <motion.h2
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-4xl font-bold mb-12 text-center text-gray-900"
          >
            Featured Projects
          </motion.h2>
          {loading ? (
            <div className="text-center text-gray-600">Loading projects...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {portfolio?.projects?.slice(0, 6).map((project: any, index: number) => (
                <ProjectCard key={project.id || index} project={project} index={index} />
              ))}
              {(!portfolio?.projects || portfolio.projects.length === 0) && (
                <div className="col-span-full text-center text-gray-600">
                  No projects yet. Check back soon!
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold mb-6 text-white">
              Let's Work Together
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Have a project in mind? I'd love to hear about it.
            </p>
            <a
              href="/blog"
              className="inline-block px-8 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
            >
              Read My Blog
            </a>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
