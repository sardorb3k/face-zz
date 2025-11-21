'use client'

import { useState, useEffect } from 'react'
import { studentsApi, Student } from '@/lib/api'
import UploadFaceModal from './UploadFaceModal'
import CameraFaceUpload from './CameraFaceUpload'

interface StudentsListProps {
  onStudentAdded?: () => void
}

export default function StudentsList({ onStudentAdded }: StudentsListProps = {}) {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadModalOpen, setUploadModalOpen] = useState(false)
  const [cameraModalOpen, setCameraModalOpen] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)

  useEffect(() => {
    loadStudents()
  }, [])

  const loadStudents = async () => {
    try {
      setLoading(true)
      const data = await studentsApi.getAll()
      setStudents(data)
    } catch (error) {
      console.error('Talabalar yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadFace = (student: Student) => {
    setSelectedStudent(student)
    setUploadModalOpen(true)
  }

  const handleDelete = async (student: Student) => {
    if (!confirm(`"${student.full_name}" talabasini o'chirishni tasdiqlaysizmi?`)) {
      return
    }

    try {
      await studentsApi.delete(student.id)
      loadStudents()
    } catch (error) {
      console.error('Talabani o\'chirishda xatolik:', error)
      alert('Talabani o\'chirishda xatolik yuz berdi')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-600">Yuklanmoqda...</div>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Talaba ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ism Familiya
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Kurs / Guruh
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Holat
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amallar
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {students.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  Talabalar topilmadi
                </td>
              </tr>
            ) : (
              students.map((student) => (
                <tr key={student.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {student.student_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {student.full_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {student.email || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {student.course && student.group
                      ? `${student.course} / ${student.group}`
                      : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        student.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {student.is_active ? 'Faol' : 'Nofaol'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setSelectedStudent(student)
                          setCameraModalOpen(true)
                        }}
                        className="text-primary-600 hover:text-primary-900 px-2 py-1 rounded"
                        title="Kamera orqali yuz yuklash"
                      >
                        📷
                      </button>
                      <button
                        onClick={() => handleUploadFace(student)}
                        className="text-gray-600 hover:text-gray-900 px-2 py-1 rounded"
                        title="Fayl orqali yuz yuklash"
                      >
                        📁
                      </button>
                      <button
                        onClick={() => handleDelete(student)}
                        className="text-red-600 hover:text-red-900 px-2 py-1 rounded"
                        title="O'chirish"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {uploadModalOpen && selectedStudent && (
        <UploadFaceModal
          student={selectedStudent}
          onClose={() => {
            setUploadModalOpen(false)
            setSelectedStudent(null)
          }}
          onSuccess={() => {
            setUploadModalOpen(false)
            setSelectedStudent(null)
            loadStudents()
          }}
        />
      )}

      {cameraModalOpen && selectedStudent && (
        <CameraFaceUpload
          student={selectedStudent}
          onClose={() => {
            setCameraModalOpen(false)
            setSelectedStudent(null)
          }}
          onSuccess={() => {
            setCameraModalOpen(false)
            setSelectedStudent(null)
            loadStudents()
          }}
        />
      )}
    </>
  )
}
