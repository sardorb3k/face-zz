'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import StudentsList from './components/StudentsList'
import AttendanceStats from './components/AttendanceStats'
import AttendanceList from './components/AttendanceList'
import AddStudentModal from './components/AddStudentModal'
import CameraStatus from './components/CameraStatus'
import Link from 'next/link'

export default function Home() {
  const { isAuthenticated, isAdmin, user, logout, loading: authLoading } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'students' | 'attendance' | 'stats'>('stats')
  const [showAddModal, setShowAddModal] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    } else if (!authLoading && isAuthenticated && user?.role === 'student') {
      // Student'lar faqat o'z dashboard'ini ko'radi
      router.push('/student')
    }
  }, [isAuthenticated, authLoading, router, user])

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !isAdmin) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Face Recognition Attendance System
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Yuz tanib olish orqali davomat tizimi
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              {isAdmin && (
                <Link
                  href="/admin"
                  className="px-4 py-2 text-sm text-white bg-purple-600 rounded hover:bg-purple-700"
                >
                  Admin Panel
                </Link>
              )}
              {user?.role === 'student' && (
                <Link
                  href="/student"
                  className="px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700"
                >
                  My Dashboard
                </Link>
              )}
              <button
                onClick={logout}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'stats'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Statistika
            </button>
            <button
              onClick={() => setActiveTab('students')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'students'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Talabalar
            </button>
            <button
              onClick={() => setActiveTab('attendance')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'attendance'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Davomat
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'stats' && (
          <div className="space-y-6">
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Davomat Statistikasi</h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <AttendanceStats />
              </div>
              <div>
                <CameraStatus />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'students' && (
          <div>
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Talabalar Ro'yxati</h2>
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
              >
                + Talaba Qo'shish
              </button>
            </div>
            <StudentsList key={refreshKey} />
          </div>
        )}

        {activeTab === 'attendance' && (
          <div>
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Davomat Ma'lumotlari</h2>
            </div>
            <AttendanceList />
          </div>
        )}
      </main>

      {/* Add Student Modal */}
      {showAddModal && (
        <AddStudentModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false)
            setActiveTab('students') // Talabalar tab'iga o'tish
            setRefreshKey(prev => prev + 1) // StudentsList yangilash
          }}
        />
      )}
    </div>
  )
}

