'use client'

import { useState, useEffect, useRef } from 'react'
import { attendanceApi, Attendance } from '@/lib/api'
import { getWebSocket, AttendanceEvent } from '@/lib/websocket'
import { format } from 'date-fns'

export default function AttendanceList() {
  const [attendances, setAttendances] = useState<Attendance[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [newCount, setNewCount] = useState(0)
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<ReturnType<typeof getWebSocket> | null>(null)

  useEffect(() => {
    // Initial load
    loadAttendances()
    
    // Setup WebSocket
    const ws = getWebSocket()
    wsRef.current = ws
    
    // Connect WebSocket
    ws.connect()
    
    // Check connection status
    const checkConnection = setInterval(() => {
      setWsConnected(ws.isConnected())
    }, 1000)
    
    // Listen for attendance events
    const unsubscribe = ws.onMessage((event: AttendanceEvent) => {
      if (event.type === 'attendance' && event.data) {
        const newAttendance: Attendance = {
          id: event.data.id,
          student_id: event.data.student_id || 0,
          detected_at: event.data.detected_at,
          location: event.data.camera?.location,
          confidence: event.data.confidence || undefined,
          image_path: event.data.image_path || undefined,
          track_id: event.data.track_id || undefined,
          student: event.data.student ? {
            id: event.data.student.id,
            student_id: event.data.student.student_id,
            full_name: event.data.student.full_name,
            is_active: true,
            created_at: new Date().toISOString()
          } : {
            id: 0,
            student_id: 'Unknown',
            full_name: 'Unknown',
            is_active: true,
            created_at: new Date().toISOString()
          }
        }
        
        // Add new attendance to the top
        setAttendances(prev => {
          // Filter out duplicates
          const existingIds = new Set(prev.map(a => a.id))
          if (existingIds.has(newAttendance.id)) {
            return prev
          }
          
          setNewCount(1)
          setTimeout(() => setNewCount(0), 3000)
          
          return [newAttendance, ...prev].slice(0, 100) // Keep max 100
        })
        
        setLastUpdate(new Date())
      }
    })
    
    return () => {
      clearInterval(checkConnection)
      unsubscribe()
      // Don't disconnect WebSocket here as it might be used by other components
      // ws.disconnect()
    }
  }, [])

  const loadAttendances = async () => {
    try {
      setLoading(true)
      const data = await attendanceApi.getAll({ limit: 100 })
      setAttendances(data)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Davomat yuklashda xatolik:', error)
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

  return (
    <div className="space-y-4">
      {/* Real-time indicator and new count */}
      <div className="flex items-center justify-between bg-white shadow rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className={`h-3 w-3 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {wsConnected ? 'WebSocket ulangan' : 'WebSocket ulanmagan'}
            </span>
          </div>
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              Oxirgi yangilanish: {format(lastUpdate, 'HH:mm:ss')}
            </span>
          )}
        </div>
        {newCount > 0 && (
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium animate-pulse">
            +{newCount} yangi davomat
          </div>
        )}
        <button
          onClick={loadAttendances}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Yangilash
        </button>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Vaqt
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Talaba
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Talaba ID
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Joylashuv
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ishonchlilik
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {attendances.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                Davomat ma'lumotlari topilmadi
              </td>
            </tr>
          ) : (
            attendances.map((attendance) => (
              <tr key={attendance.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {format(new Date(attendance.detected_at), 'dd.MM.yyyy HH:mm:ss')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {attendance.student?.full_name || 'Noma\'lum'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {attendance.student?.student_id || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {attendance.camera?.location || attendance.camera?.name || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {attendance.confidence
                    ? `${(attendance.confidence * 100).toFixed(1)}%`
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

