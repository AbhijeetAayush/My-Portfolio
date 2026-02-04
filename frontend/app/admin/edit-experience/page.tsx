'use client'

import AdminLayout from '@/components/AdminLayout'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'

interface Experience {
  id?: string
  title: string
  position: string
  company: string
  organization: string
  description: string
  start_date: number
  end_date: number | null
  technologies: string[]
}

export default function EditExperiencePage() {
  const [loading, setLoading] = useState(true)
  const [experience, setExperience] = useState<Experience[]>([])
  const [saving, setSaving] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [formData, setFormData] = useState<Experience>({
    title: '',
    position: '',
    company: '',
    organization: '',
    description: '',
    start_date: Math.floor(Date.now() / 1000),
    end_date: null,
    technologies: [],
  })
  const [techInput, setTechInput] = useState('')

  useEffect(() => {
    fetchExperience()
  }, [])

  const fetchExperience = async () => {
    try {
      const response = await portfolioAPI.get()
      setExperience(response.data.data.experience || [])
    } catch (err) {
      console.error('Error fetching experience:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await portfolioAPI.update({ experience })
      alert('Experience updated successfully!')
      setEditingIndex(null)
    } catch (err) {
      console.error('Error saving experience:', err)
      alert('Failed to save experience')
    } finally {
      setSaving(false)
    }
  }

  const handleAdd = () => {
    const newExp: Experience = {
      id: Date.now().toString(),
      title: '',
      position: '',
      company: '',
      organization: '',
      description: '',
      start_date: Math.floor(Date.now() / 1000),
      end_date: null,
      technologies: [],
    }
    setExperience([...experience, newExp])
    setEditingIndex(experience.length)
    setFormData(newExp)
  }

  const handleEdit = (index: number) => {
    setEditingIndex(index)
    setFormData(experience[index])
  }

  const handleUpdate = () => {
    if (editingIndex === null) return
    const updated = [...experience]
    updated[editingIndex] = { ...formData }
    setExperience(updated)
    setEditingIndex(null)
  }

  const handleDelete = (index: number) => {
    if (confirm('Are you sure you want to delete this experience entry?')) {
      const updated = experience.filter((_, i) => i !== index)
      setExperience(updated)
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

  const formatDateForInput = (timestamp: number | null) => {
    if (!timestamp) return ''
    try {
      return new Date(timestamp * 1000).toISOString().split('T')[0]
    } catch {
      return ''
    }
  }

  const parseDateToTimestamp = (dateString: string) => {
    if (!dateString) return null
    return Math.floor(new Date(dateString).getTime() / 1000)
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
          <h1 className="text-3xl font-bold text-gray-900">Edit Experience</h1>
          <div className="flex gap-4">
            <button
              onClick={handleAdd}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Add Experience
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
          {experience.map((exp, index) => (
            <div key={exp.id || index} className="bg-white p-6 rounded-lg shadow">
              {editingIndex === index ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    placeholder="Title/Position"
                    value={formData.title || formData.position}
                    onChange={(e) =>
                      setFormData({ ...formData, title: e.target.value, position: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Company/Organization"
                    value={formData.company || formData.organization}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        company: e.target.value,
                        organization: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                  <textarea
                    placeholder="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    rows={4}
                  />
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Start Date</label>
                      <input
                        type="date"
                        value={formatDateForInput(formData.start_date)}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            start_date: parseDateToTimestamp(e.target.value) || formData.start_date,
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">End Date (leave empty if current)</label>
                      <input
                        type="date"
                        value={formatDateForInput(formData.end_date)}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            end_date: parseDateToTimestamp(e.target.value),
                          })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>
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
                    <h3 className="text-xl font-semibold">
                      {exp.title || exp.position || 'Untitled'}
                    </h3>
                    <p className="text-primary-600 font-semibold">
                      {exp.company || exp.organization}
                    </p>
                    <p className="text-gray-600 mt-2">{exp.description}</p>
                    {exp.technologies && exp.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {exp.technologies.map((tech, i) => (
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
          {experience.length === 0 && (
            <div className="text-center py-12 text-gray-600">
              No experience entries yet. Click "Add Experience" to get started.
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  )
}
