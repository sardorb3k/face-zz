'use client'

import { useState, useEffect } from 'react'
import { attendanceApi, AttendanceStats as Stats } from '@/lib/api'
import { format } from 'date-fns'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function AttendanceStats() {
  const [stats, setStats] = useState<Stats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await attendanceApi.getStats()
      setStats(data)
    } catch (error) {
      console.error('Statistika yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-600">Yuklanmoqda...</div>
      </div>
    )
  }

  const chartData = stats
    .sort((a, b) => b.total_attendances - a.total_attendances)
    .slice(0, 10)
    .map((stat) => ({
      name: stat.student_name,
      davomat: stat.total_attendances,
    }))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Jami Talabalar</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{stats.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Jami Davomatlar</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {stats.reduce((sum, stat) => sum + stat.total_attendances, 0)}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">O'rtacha Davomat</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {stats.length > 0
              ? Math.round(
                  stats.reduce((sum, stat) => sum + stat.total_attendances, 0) / stats.length
                )
              : 0}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Top 10 Talabalar (Davomat bo'yicha)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="davomat" fill="#0ea5e9" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stats Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Talaba
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Jami Davomat
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Oxirgi Davomat
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {stats.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-6 py-4 text-center text-gray-500">
                  Ma'lumot topilmadi
                </td>
              </tr>
            ) : (
              stats
                .sort((a, b) => b.total_attendances - a.total_attendances)
                .map((stat) => (
                  <tr key={stat.student_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {stat.student_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {stat.total_attendances}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {stat.last_attendance
                        ? format(new Date(stat.last_attendance), 'dd.MM.yyyy HH:mm')
                        : '-'}
                    </td>
                  </tr>
                ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

