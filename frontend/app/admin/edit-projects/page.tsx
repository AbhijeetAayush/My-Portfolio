'use client'

import AdminLayout from '@/components/AdminLayout'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'

interface Project {
  id?: string
  title: string
  description: string
  image_url: string
  technologies: string[]
  link: string
}

export default function EditProjectsPage() {
  const [loading, setLoading] = useState(true)
  const [projects, setProjects] = useState<Project[]>([])
  const [saving, setSaving] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [formData, setFormData] = useState<Project>({
    title: '',
    description: '',
    image_url: '',
    technologies: [],
    link: '',
  })
  const [techInput, setTechInput] = useState('')

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await portfolioAPI.get()
      setProjects(response.data.data.projects || [])
    } catch (err) {
      console.error('Error fetching projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await portfolioAPI.update({ projects })
      alert('Projects updated successfully!')
      setEditingIndex(null)
    } catch (err) {
      console.error('Error saving projects:', err)
      alert('Failed to save projects')
    } finally {
      setSaving(false)
    }
  }

  const handleAdd = () => {
    const newProject: Project = {
      id: Date.now().toString(),
      title: '',
      description: '',
      image_url: '',
      technologies: [],
      link: '',
    }
    setProjects([...projects, newProject])
    setEditingIndex(projects.length)
    setFormData(newProject)
  }

  const handleEdit = (index: number) => {
    setEditingIndex(index)
    setFormData(projects[index])
  }

  const handleUpdate = () => {
    if (editingIndex === null) return
    const updated = [...projects]
    updated[editingIndex] = { ...formData }
    setProjects(updated)
    setEditingIndex(null)
  }

  const handleDelete = (index: number) => {
    if (confirm('Are you sure you want to delete this project?')) {
      const updated = projects.filter((_, i) => i !== index)
      setProjects(updated)
      if (editingIndex === index) {
        setEditingIndex(null)
      }
    }
  }

  const addTechnology = () => {
    if (techInput.trim()) {
      setFormData({
        ...formData,
        technologies: [...formData.technologies, techInput.trim()],
      })
      setTechInput('')
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Edit Projects</h1>
          <div className="flex gap-4">
            <button
              onClick={handleAdd}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Add Project
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save All'}
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {projects.map((project, index) => (
            <div key={project.id || index} className="bg-white p-6 rounded-lg shadow">
              {editingIndex === index ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    placeholder="Title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <textarea
                    placeholder="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    rows={3}
                  />
                  <input
                    type="url"
                    placeholder="Image URL"
                    value={formData.image_url}
                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="url"
                    placeholder="Project Link"
                    value={formData.link}
                    onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <div>
                    <div className="flex gap-2 mb-2">
                      <input
                        type="text"
                        placeholder="Add technology"
                        value={techInput}
                        onChange={(e) => setTechInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && addTechnology()}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={addTechnology}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg"
                      >
                        Add
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {formData.technologies.map((tech, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center gap-2"
                        >
                          {tech}
                          <button
                            onClick={() => {
                              setFormData({
                                ...formData,
                                technologies: formData.technologies.filter((_, idx) => idx !== i),
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
                  <div className="flex gap-2">
                    <button
                      onClick={handleUpdate}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg"
                    >
                      Update
                    </button>
                    <button
                      onClick={() => setEditingIndex(null)}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold">{project.title || 'Untitled'}</h3>
                    <p className="text-gray-600 mt-2">{project.description}</p>
                    {project.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {project.technologies.map((tech, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(index)}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(index)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {projects.length === 0 && (
            <div className="text-center py-12 text-gray-600">
              No projects yet. Click "Add Project" to get started.
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  )
}
