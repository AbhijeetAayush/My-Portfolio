'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'
import ProjectCard from '@/components/ProjectCard'

export default function ProjectsPage() {
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
        <div className="container mx-auto px-6 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-5xl font-bold mb-6"
          >
            My Projects
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-white/90 max-w-2xl mx-auto"
          >
            A collection of my recent work and projects
          </motion.p>
        </div>
      </section>

      {/* Projects Grid */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          {loading ? (
            <div className="text-center text-gray-600">Loading projects...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {portfolio?.projects?.map((project: any, index: number) => (
                <ProjectCard key={project.id || index} project={project} index={index} />
              ))}
              {(!portfolio?.projects || portfolio.projects.length === 0) && (
                <div className="col-span-full text-center text-gray-600 py-20">
                  <p className="text-xl">No projects yet. Check back soon!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
