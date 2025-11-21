'use client'

import { useState, useRef, useEffect } from 'react'
import { uploadApi, Student } from '@/lib/api'
import { FaceDetection } from '@mediapipe/face_detection'
import { Camera } from '@mediapipe/camera_utils'

interface CameraFaceUploadProps {
  student: Student
  onClose: () => void
  onSuccess: () => void
}

type Step = 'camera' | 'testing' | 'success'

interface FaceDetectionResult {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

export default function CameraFaceUpload({ student, onClose, onSuccess }: CameraFaceUploadProps) {
  const [step, setStep] = useState<Step>('camera')
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [testResult, setTestResult] = useState<{
    success: boolean
    message: string
    confidence?: number
  } | null>(null)
  const [faceDetected, setFaceDetected] = useState(false)
  const [faceDetectionResult, setFaceDetectionResult] = useState<FaceDetectionResult | null>(null)
  const [autoCaptureCountdown, setAutoCaptureCountdown] = useState<number | null>(null)
  const [isAutoCapturing, setIsAutoCapturing] = useState(false)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const faceDetectionRef = useRef<FaceDetection | null>(null)
  const cameraRef = useRef<Camera | null>(null)
  const autoCaptureTimerRef = useRef<NodeJS.Timeout | null>(null)
  const countdownTimerRef = useRef<NodeJS.Timeout | null>(null)

  // Face Detection ni yuklash
  useEffect(() => {
    if (step === 'camera' && !faceDetectionRef.current) {
      initializeFaceDetection()
    }

    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop()
        cameraRef.current = null
      }
      if (faceDetectionRef.current) {
        faceDetectionRef.current.close()
        faceDetectionRef.current = null
      }
      // Timer'larni tozalash
      if (autoCaptureTimerRef.current) {
        clearTimeout(autoCaptureTimerRef.current)
        autoCaptureTimerRef.current = null
      }
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
        countdownTimerRef.current = null
      }
    }
  }, [step])

  // Avtomatik rasm olish timer'i
  useEffect(() => {
    // Timer'larni tozalash
    if (autoCaptureTimerRef.current) {
      clearTimeout(autoCaptureTimerRef.current)
      autoCaptureTimerRef.current = null
    }
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current)
      countdownTimerRef.current = null
    }
    setAutoCaptureCountdown(null)

    // Yuz aniqlandi-yu va kamera bosqichida bo'lsa, avtomatik rasm olish
    if (faceDetected && step === 'camera' && !isAutoCapturing) {
      setIsAutoCapturing(true)
      let countdown = 3 // 3 soniya countdown

      // Countdown ko'rsatish
      setAutoCaptureCountdown(countdown)
      countdownTimerRef.current = setInterval(() => {
        countdown -= 1
        setAutoCaptureCountdown(countdown)
        if (countdown <= 0) {
          if (countdownTimerRef.current) {
            clearInterval(countdownTimerRef.current)
            countdownTimerRef.current = null
          }
        }
      }, 1000)

      // 3 soniya o'tgach avtomatik rasm olish
      autoCaptureTimerRef.current = setTimeout(() => {
        setAutoCaptureCountdown(null)
        autoCapturePhoto()
      }, 3000)
    } else if (!faceDetected) {
      // Yuz aniqlanmadi-yu, timer'larni tozalash
      setIsAutoCapturing(false)
      setAutoCaptureCountdown(null)
    }

    return () => {
      if (autoCaptureTimerRef.current) {
        clearTimeout(autoCaptureTimerRef.current)
      }
      if (countdownTimerRef.current) {
        clearInterval(countdownTimerRef.current)
      }
    }
  }, [faceDetected, step])

  const initializeFaceDetection = async () => {
    try {
      const faceDetection = new FaceDetection({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`
        }
      })

      faceDetection.setOptions({
        model: 'short', // 'short' tez, 'full' aniqroq
        minDetectionConfidence: 0.5
      })

      faceDetection.onResults((results) => {
        if (overlayCanvasRef.current && videoRef.current) {
          const canvas = overlayCanvasRef.current
          const ctx = canvas.getContext('2d')
          if (!ctx) return

          // Canvas o'lchamini video o'lchamiga moslashtirish
          canvas.width = videoRef.current.videoWidth || 640
          canvas.height = videoRef.current.videoHeight || 480

          // Canvas'ni tozalash
          ctx.clearRect(0, 0, canvas.width, canvas.height)

          if (results.detections && results.detections.length > 0) {
            const detection = results.detections[0]
            const bbox = detection.boundingBox
            
            // Yuz aniqlandi
            setFaceDetected(true)
            setFaceDetectionResult({
              x: bbox.xCenter * canvas.width - (bbox.width * canvas.width) / 2,
              y: bbox.yCenter * canvas.height - (bbox.height * canvas.height) / 2,
              width: bbox.width * canvas.width,
              height: bbox.height * canvas.height,
              confidence: detection.score || 0
            })

            // Bounding box chizish
            ctx.strokeStyle = '#00ff00'
            ctx.lineWidth = 3
            ctx.strokeRect(
              bbox.xCenter * canvas.width - (bbox.width * canvas.width) / 2,
              bbox.yCenter * canvas.height - (bbox.height * canvas.height) / 2,
              bbox.width * canvas.width,
              bbox.height * canvas.height
            )

            // Confidence ko'rsatish
            ctx.fillStyle = '#00ff00'
            ctx.font = '16px Arial'
            ctx.fillText(
              `Yuz aniqlandi: ${((detection.score || 0) * 100).toFixed(1)}%`,
              bbox.xCenter * canvas.width - (bbox.width * canvas.width) / 2,
              bbox.yCenter * canvas.height - (bbox.height * canvas.height) / 2 - 10
            )
          } else {
            setFaceDetected(false)
            setFaceDetectionResult(null)
          }
        }
      })

      faceDetectionRef.current = faceDetection

      // Camera'ni ishga tushirish
      if (videoRef.current) {
        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (videoRef.current && faceDetectionRef.current) {
              await faceDetectionRef.current.send({ image: videoRef.current })
            }
          },
          width: 1280,
          height: 720
        })
        cameraRef.current = camera
        camera.start()
      }
    } catch (err) {
      console.error('Face detection initialization error:', err)
      // Agar MediaPipe yuklanmasa, oddiy kamera rejimiga o'tamiz
      startSimpleCamera()
    }
  }

  const startSimpleCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
      }
    } catch (err) {
      setError('Kameraga kirish imkoni yo\'q. Iltimos, ruxsat bering.')
      console.error('Camera error:', err)
    }
  }

  const stopCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.stop()
      cameraRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    if (faceDetectionRef.current) {
      faceDetectionRef.current.close()
      faceDetectionRef.current = null
    }
    setFaceDetected(false)
    setFaceDetectionResult(null)
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    // Yuz aniqlandi-yu tekshirish
    if (!faceDetected) {
      setError('Iltimos, yuzingizni kameraga to\'g\'ri qilib qo\'ying. Yuz aniqlandi-yu ko\'rsatilganda rasm oling.')
      return
    }

    // Timer'larni tozalash
    if (autoCaptureTimerRef.current) {
      clearTimeout(autoCaptureTimerRef.current)
      autoCaptureTimerRef.current = null
    }
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current)
      countdownTimerRef.current = null
    }
    setIsAutoCapturing(false)
    setAutoCaptureCountdown(null)

    doCapturePhoto()
  }

  const autoCapturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return
    
    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    // Canvas o'lchamini video o'lchamiga moslashtirish
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Rasmni chizish
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Base64 formatida olish
    const imageData = canvas.toDataURL('image/jpeg', 0.95)
    setCapturedImage(imageData)
    setStep('testing')
    stopCamera()
    
    // Avtomatik test qilish - rasm olingandan keyin
    setTimeout(async () => {
      await performTestAndUpload(imageData)
    }, 500)
  }

  const performTestAndUpload = async (imageData: string) => {
    setLoading(true)
    setError('')
    setTestResult(null)

    try {
      // Base64 dan File ga o'tkazish
      const blob = await fetch(imageData).then(res => res.blob())
      const file = new File([blob], `student_${student.id}_face.jpg`, { type: 'image/jpeg' })

      // 1. Avval test qilish
      const testResult = await uploadApi.testFace(student.id, file)

      if (!testResult.success) {
        setTestResult({
          success: false,
          message: testResult.message || 'Yuz aniqlanmadi'
        })
        setLoading(false)
        return
      }

      // 2. Test muvaffaqiyatli bo'lsa, yuklash
      const uploadResult = await uploadApi.uploadFace(student.id, file)

      if (uploadResult.success && uploadResult.embedding_created) {
        setTestResult({
          success: true,
          message: 'Yuz muvaffaqiyatli yuklandi va embedding yaratildi!',
          confidence: testResult.confidence || 1.0
        })
        setStep('success')
      } else {
        setTestResult({
          success: false,
          message: uploadResult.message || 'Yuklashda xatolik yuz berdi'
        })
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Xatolik yuz berdi'
      setError(errorMessage)
      setTestResult({
        success: false,
        message: errorMessage
      })
    } finally {
      setLoading(false)
    }
  }

  const doCapturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    // Canvas o'lchamini video o'lchamiga moslashtirish
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Rasmni chizish
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Base64 formatida olish
    const imageData = canvas.toDataURL('image/jpeg', 0.95)
    setCapturedImage(imageData)
    setStep('testing')
    stopCamera()
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    setTestResult(null)
    setError('')
    setIsAutoCapturing(false)
    setAutoCaptureCountdown(null)
    // Timer'larni tozalash
    if (autoCaptureTimerRef.current) {
      clearTimeout(autoCaptureTimerRef.current)
      autoCaptureTimerRef.current = null
    }
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current)
      countdownTimerRef.current = null
    }
    setStep('camera')
  }

  const testAndUpload = async () => {
    if (!capturedImage) return

    setLoading(true)
    setError('')
    setTestResult(null)

    try {
      // Base64 dan File ga o'tkazish
      const blob = await fetch(capturedImage).then(res => res.blob())
      const file = new File([blob], `student_${student.id}_face.jpg`, { type: 'image/jpeg' })

      // 1. Avval test qilish
      const testResult = await uploadApi.testFace(student.id, file)

      if (!testResult.success) {
        setTestResult({
          success: false,
          message: testResult.message || 'Yuz aniqlanmadi'
        })
        setLoading(false)
        return
      }

      // 2. Test muvaffaqiyatli bo'lsa, yuklash
      const uploadResult = await uploadApi.uploadFace(student.id, file)

      if (uploadResult.success && uploadResult.embedding_created) {
        setTestResult({
          success: true,
          message: 'Yuz muvaffaqiyatli yuklandi va embedding yaratildi!',
          confidence: testResult.confidence || 1.0
        })
        setStep('success')
      } else {
        setTestResult({
          success: false,
          message: uploadResult.message || 'Yuklashda xatolik yuz berdi'
        })
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Xatolik yuz berdi'
      setError(errorMessage)
      setTestResult({
        success: false,
        message: errorMessage
      })
    } finally {
      setLoading(false)
    }
  }


  const handleFinish = () => {
    onSuccess()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">
          Kamera orqali Yuz Yuklash - {student.full_name}
        </h2>

        {/* Step 1: Camera */}
        {step === 'camera' && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-blue-900 mb-2">📸 1-bosqich: Avtomatik Yuzni Olish</h3>
              <p className="text-sm text-blue-700">
                Kameraga qarang va to'liq yuzingiz ko'rinishini ta'minlang. 
                Yuz aniqlandi-yu, <strong>3 soniya</strong> o'tgach avtomatik rasm olinadi va test qilinadi.
              </p>
            </div>

            {error && (
              <div className="p-3 bg-red-100 text-red-700 rounded">{error}</div>
            )}

            <div className="relative bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-auto max-h-[480px]"
              />
              {/* Real-time face detection overlay */}
              <canvas
                ref={overlayCanvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
                style={{ objectFit: 'contain' }}
              />
              {/* Face guide overlay (yuz aniqlanmaganda ko'rsatiladi) */}
              {!faceDetected && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="border-2 border-yellow-400 rounded-full w-64 h-80 opacity-30 animate-pulse"></div>
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-yellow-500 bg-opacity-75 text-white px-4 py-2 rounded-lg">
                    ⚠️ Yuzingizni kameraga qarab turing
                  </div>
                </div>
              )}
              {/* Yuz aniqlandi-yu ko'rsatish */}
              {faceDetected && faceDetectionResult && (
                <>
                  <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-green-500 bg-opacity-90 text-white px-4 py-2 rounded-lg shadow-lg z-10">
                    ✅ Yuz aniqlandi! {(faceDetectionResult.confidence * 100).toFixed(1)}%
                  </div>
                  {/* Avtomatik rasm olish countdown */}
                  {autoCaptureCountdown !== null && autoCaptureCountdown > 0 && (
                    <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-blue-500 bg-opacity-90 text-white px-6 py-3 rounded-lg shadow-lg z-10 text-center">
                      <div className="text-3xl font-bold mb-1">{autoCaptureCountdown}</div>
                      <div className="text-sm">Avtomatik rasm olinmoqda...</div>
                    </div>
                  )}
                  {autoCaptureCountdown === 0 && (
                    <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-blue-500 bg-opacity-90 text-white px-6 py-3 rounded-lg shadow-lg z-10 text-center">
                      <div className="text-lg font-bold">📸 Rasm olinmoqda...</div>
                    </div>
                  )}
                </>
              )}
            </div>

            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Bekor qilish
              </button>
              <button
                type="button"
                onClick={capturePhoto}
                disabled={!faceDetected}
                className={`px-6 py-3 rounded-md font-semibold ${
                  faceDetected
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                }`}
              >
                {faceDetected ? '📸 Rasm Olish' : '⏳ Yuzni Kutmoqda...'}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Testing */}
        {step === 'testing' && capturedImage && (
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-yellow-900 mb-2">🔍 2-bosqich: Avtomatik Test Qilish</h3>
              <p className="text-sm text-yellow-700">
                Rasm avtomatik olingan. Yuz embedding yaratilmoqda va test qilinmoqda. 
                Agar yuz to'g'ri aniqlangan bo'lsa, "Bo'ldi" tugmasini bosing.
              </p>
            </div>

            <div className="relative bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={capturedImage}
                alt="Captured face"
                className="w-full h-auto max-h-[480px] object-contain"
              />
            </div>

            {testResult && (
              <div className={`p-4 rounded-lg ${
                testResult.success 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}>
                <div className="flex items-center space-x-2">
                  {testResult.success ? (
                    <>
                      <span className="text-2xl">✅</span>
                      <div>
                        <p className="font-semibold text-green-900">{testResult.message}</p>
                        {testResult.confidence && (
                          <p className="text-sm text-green-700">
                            Ishonchlilik: {(testResult.confidence * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    </>
                  ) : (
                    <>
                      <span className="text-2xl">❌</span>
                      <div>
                        <p className="font-semibold text-red-900">{testResult.message}</p>
                        <p className="text-sm text-red-700">
                          Iltimos, qayta rasm oling va yaxshi yoritilgan joyda bo'ling.
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {error && !testResult && (
              <div className="p-3 bg-red-100 text-red-700 rounded">{error}</div>
            )}

            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={retakePhoto}
                disabled={loading}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50"
              >
                🔄 Qayta Olish
              </button>
              <div className="flex space-x-3">
                {!testResult && !loading && (
                  <button
                    type="button"
                    onClick={testAndUpload}
                    disabled={loading}
                    className="px-6 py-3 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 font-semibold"
                  >
                    🔍 Qayta Test Qilish
                  </button>
                )}
                {loading && (
                  <div className="px-6 py-3 bg-yellow-600 text-white rounded-md font-semibold">
                    ⏳ Avtomatik test qilinmoqda...
                  </div>
                )}
                {testResult?.success && (
                  <button
                    type="button"
                    onClick={handleFinish}
                    className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-semibold"
                  >
                    ✅ Bo'ldi
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Success */}
        {step === 'success' && (
          <div className="space-y-4 text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-2xl font-semibold text-green-600 mb-2">
              Muvaffaqiyatli!
            </h3>
            <p className="text-gray-700 mb-6">
              {student.full_name} uchun yuz rasmi muvaffaqiyatli yuklandi va embedding yaratildi.
            </p>
            <button
              type="button"
              onClick={handleFinish}
              className="px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 font-semibold"
            >
              Yopish
            </button>
          </div>
        )}

        {/* Hidden canvas for capturing */}
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  )
}

