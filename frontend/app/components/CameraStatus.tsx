'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Camera {
  id: number
  name: string
  camera_type: string
  is_active: boolean
  location: string | null
}

export default function CameraStatus() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCameras()
    const interval = setInterval(loadCameras, 5000) // Har 5 soniyada yangilash
    return () => clearInterval(interval)
  }, [])

  const loadCameras = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cameras`)
      setCameras(response.data)
    } catch (error) {
      console.error('Kamerani yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <div className="text-gray-600">Yuklanmoqda...</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Kamera Holati</h3>
      <div className="space-y-2">
        {cameras.length === 0 ? (
          <p className="text-gray-500 text-sm">Kamera topilmadi</p>
        ) : (
          cameras.map((camera) => (
            <div key={camera.id} className="flex items-center justify-between p-2 border rounded">
              <div>
                <span className="font-medium">{camera.name}</span>
                <span className="text-sm text-gray-500 ml-2">
                  ({camera.camera_type})
                </span>
                {camera.location && (
                  <span className="text-sm text-gray-500 ml-2">- {camera.location}</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <div
                  className={`h-3 w-3 rounded-full ${
                    camera.is_active ? 'bg-green-500' : 'bg-red-500'
                  }`}
                ></div>
                <span className="text-sm text-gray-600">
                  {camera.is_active ? 'Faol' : 'Nofaol'}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

