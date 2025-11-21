'use client'

import { useState } from 'react'
import { uploadApi, Student } from '@/lib/api'

interface UploadFaceModalProps {
  student: Student
  onClose: () => void
  onSuccess: () => void
}

export default function UploadFaceModal({ student, onClose, onSuccess }: UploadFaceModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
      
      // Preview yaratish
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Iltimos, rasm tanlang')
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await uploadApi.uploadFace(student.id, file)
      if (result.success) {
        setSuccess(true)
        setTimeout(() => {
          onSuccess()
        }, 2000)
      } else {
        setError(result.message || 'Xatolik yuz berdi')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Xatolik yuz berdi')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">
          Yuz Rasmini Yuklash - {student.full_name}
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
            Yuz rasmi muvaffaqiyatli yuklandi va embedding yaratildi!
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rasm Tanlash
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          {preview && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Ko'rib chiqish:</p>
              <img
                src={preview}
                alt="Preview"
                className="w-full h-64 object-contain border border-gray-300 rounded"
              />
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Yopish
            </button>
            <button
              type="submit"
              disabled={loading || !file || success}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Yuklanmoqda...' : 'Yuklash'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

