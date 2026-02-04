'use client'

import AdminLayout from '@/components/AdminLayout'
import { useEffect, useState } from 'react'
import { portfolioAPI } from '@/lib/api'

export default function EditProfilePage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    profile_pic_url: '',
    bio: '',
    email: '',
    social_links: {
      twitter: '',
      linkedin: '',
      github: '',
      instagram: '',
    },
    about_content: '',
  })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await portfolioAPI.get()
      const data = response.data.data
      setFormData({
        profile_pic_url: data.profile_pic_url || '',
        bio: data.bio || '',
        email: data.email || '',
        social_links: data.social_links || {
          twitter: '',
          linkedin: '',
          github: '',
          instagram: '',
        },
        about_content: data.about_content || '',
      })
    } catch (err) {
      console.error('Error fetching profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      await portfolioAPI.update(formData)
      alert('Profile updated successfully!')
    } catch (err: any) {
      console.error('Error updating profile:', err)
      alert('Failed to update profile. Please try again.')
    } finally {
      setSaving(false)
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
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Edit Profile</h1>

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Profile Picture URL (Cloudinary)
            </label>
            <input
              type="url"
              value={formData.profile_pic_url}
              onChange={(e) => setFormData({ ...formData, profile_pic_url: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="https://res.cloudinary.com/..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
            <input
              type="text"
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Short bio"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Social Links</label>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="url"
                value={formData.social_links.twitter}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    social_links: { ...formData.social_links, twitter: e.target.value },
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Twitter URL"
              />
              <input
                type="url"
                value={formData.social_links.linkedin}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    social_links: { ...formData.social_links, linkedin: e.target.value },
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="LinkedIn URL"
              />
              <input
                type="url"
                value={formData.social_links.github}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    social_links: { ...formData.social_links, github: e.target.value },
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="GitHub URL"
              />
              <input
                type="url"
                value={formData.social_links.instagram}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    social_links: { ...formData.social_links, instagram: e.target.value },
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Instagram URL"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">About Content (HTML)</label>
            <textarea
              value={formData.about_content}
              onChange={(e) => setFormData({ ...formData, about_content: e.target.value })}
              rows={10}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
              placeholder="<p>Your about content here...</p>"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </AdminLayout>
  )
}
