"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import FaceVerificationCamera from "../components/FaceVerificationCamera";

export default function StudentDashboard() {
  const { user, isAuthenticated, isStudent, logout, getAuthHeaders, loading: authLoading } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<any>(null);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [loadingAttendance, setLoadingAttendance] = useState(false);
  const [activeTab, setActiveTab] = useState<"attendance" | "verification">("attendance");
  const [showCamera, setShowCamera] = useState(false);

  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) {
      return;
    }
    
    // Check authentication
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    
    // Check if user is student
    if (!isStudent) {
      router.push("/");
      return;
    }
    
    // Load attendance if user is authenticated student
    if (user?.student_id) {
      loadMyAttendance();
    }
  }, [isAuthenticated, isStudent, authLoading, router, user]);

  const loadMyAttendance = async () => {
    if (!user?.student_id) return;
    
    setLoadingAttendance(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/attendance/?student_id=${user.student_id}&limit=100`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAttendance(data);
      }
    } catch (error) {
      console.error("Error loading attendance:", error);
    } finally {
      setLoadingAttendance(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
    }
  };

  const handleCameraCapture = async (imageBlob: Blob) => {
    // Don't close camera immediately - wait for all images
    const capturedFile = new File([imageBlob], `face_${Date.now()}.jpg`, { type: "image/jpeg" });
    setMessage(null);
    
    // Auto-upload after capture
    setUploading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append("file", capturedFile);

      const headers = getAuthHeaders();
      delete headers["Content-Type"]; // Let browser set it for FormData

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/verification/verify`,
        {
          method: "POST",
          headers: {
            ...headers,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      // Update status after each upload
      setVerificationStatus(data);
      
      // If this is the last image or embedding was created, close camera
      if (data.image_uploaded || data.is_match) {
        setShowCamera(false);
        setMessage({
          type: "success",
          text: data.message || "Yuz rasmlari muvaffaqiyatli yuklandi!",
        });
      } else {
        setMessage({
          type: "info",
          text: `Rasm yuklandi. Yana rasm olinmoqda...`,
        });
      }
    } catch (error: any) {
      setMessage({ type: "error", text: error.message || "Upload failed" });
    } finally {
      setUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: "error", text: "Please select a file" });
      return;
    }

    setUploading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const headers = getAuthHeaders();
      delete headers["Content-Type"]; // Let browser set it for FormData

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/verification/verify`,
        {
          method: "POST",
          headers: {
            ...headers,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setVerificationStatus(data);
      setMessage({
        type: data.is_match ? "success" : "error",
        text: data.message || (data.is_match ? "Face verified successfully!" : "Face does not match"),
      });
    } catch (error: any) {
      setMessage({ type: "error", text: error.message || "Upload failed" });
    } finally {
      setUploading(false);
    }
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated or not student
  if (!isAuthenticated || !isStudent) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-800">Student Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab("attendance")}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === "attendance"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Mening Davomatim
              </button>
              <button
                onClick={() => setActiveTab("verification")}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === "verification"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Yuzni Tasdiqlash
              </button>
            </nav>
          </div>
        </div>

        {/* Attendance Tab */}
        {activeTab === "attendance" && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Mening Davomatim</h2>
              <button
                onClick={loadMyAttendance}
                disabled={loadingAttendance}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loadingAttendance ? "Yuklanmoqda..." : "Yangilash"}
              </button>
            </div>

            {loadingAttendance ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Yuklanmoqda...</p>
              </div>
            ) : attendance.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">Hozircha davomat ma'lumotlari yo'q</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sana va Vaqt
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Kamera
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Aniqlik
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {attendance.map((record) => (
                      <tr key={record.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(record.detected_at).toLocaleString("uz-UZ")}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.camera?.name || "Noma'lum"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {record.confidence
                            ? (record.confidence * 100).toFixed(1) + "%"
                            : "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {attendance.length > 0 && (
              <div className="mt-4 text-sm text-gray-600">
                Jami: <strong>{attendance.length}</strong> ta davomat
              </div>
            )}
          </div>
        )}

        {/* Verification Tab */}
        {activeTab === "verification" && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Yuzni Tasdiqlash</h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Yuzingizning rasmini yuklang
                </label>
                <div className="flex space-x-4 mb-2">
                  <button
                    onClick={() => setShowCamera(true)}
                    type="button"
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
                  >
                    <span>📷</span>
                    <span>Camera orqali</span>
                  </button>
                  <div className="flex-1">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>
                </div>
                <p className="mt-1 text-sm text-gray-500">
                  Camera orqali yoki fayl yuklash orqali yuzingizni tasdiqlang
                </p>
              </div>

              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? "Tekshirilmoqda..." : "Yuzni Tasdiqlash"}
              </button>

              {message && (
                <div
                  className={`p-4 rounded-lg ${
                    message.type === "success"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {message.text}
                </div>
              )}

              {verificationStatus && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold mb-2">Tasdiqlash Tafsilotlari:</h3>
                  
                  {/* Show message if available */}
                  {verificationStatus.message && (
                    <div className={`mb-3 p-3 rounded-lg ${
                      verificationStatus.image_uploaded
                        ? "bg-green-50 border border-green-200"
                        : verificationStatus.message.includes("yuklandi") || verificationStatus.message.includes("yaratildi")
                        ? "bg-green-50 border border-green-200"
                        : verificationStatus.is_match 
                        ? "bg-green-50 border border-green-200"
                        : verificationStatus.message.includes("No face data") || verificationStatus.message.includes("5 ta rasm")
                        ? "bg-yellow-50 border border-yellow-200"
                        : "bg-red-50 border border-red-200"
                    }`}>
                      <p className={`text-sm ${
                        verificationStatus.image_uploaded
                          ? "text-green-800"
                          : verificationStatus.message.includes("yuklandi") || verificationStatus.message.includes("yaratildi")
                          ? "text-green-800"
                          : verificationStatus.is_match
                          ? "text-green-800"
                          : verificationStatus.message.includes("No face data") || verificationStatus.message.includes("5 ta rasm")
                          ? "text-yellow-800"
                          : "text-red-800"
                      }`}>
                        {verificationStatus.image_uploaded && "✅ "}
                        {verificationStatus.message.includes("yuklandi") && "✅ "}
                        {verificationStatus.message.includes("yaratildi") && "✅ "}
                        {verificationStatus.message.includes("No face data") && "⚠️ "}
                        {verificationStatus.message}
                      </p>
                    </div>
                  )}
                  
                  {verificationStatus.confidence !== undefined && 
                   verificationStatus.confidence !== null && 
                   verificationStatus.confidence > 0 && (
                    <p className="text-sm">
                      <strong>Aniqlik:</strong> {(verificationStatus.confidence * 100).toFixed(2)}%
                    </p>
                  )}
                  
                  {(verificationStatus.confidence === undefined || 
                    verificationStatus.confidence === null || 
                    verificationStatus.confidence === 0) && 
                   !verificationStatus.image_uploaded && (
                    <p className="text-sm">
                      <strong>Aniqlik:</strong> N/A
                    </p>
                  )}
                  
                  {verificationStatus.image_uploaded && (
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800 font-semibold">
                        🎉 Muvaffaqiyatli!
                      </p>
                      <p className="text-sm text-blue-700 mt-1">
                        Endi siz davomat olishingiz mumkin. Video kameralar sizni avtomatik aniqlaydi.
                      </p>
                    </div>
                  )}
                  
                  {!verificationStatus.image_uploaded && 
                   !verificationStatus.message?.includes("yuklandi") &&
                   !verificationStatus.message?.includes("yaratildi") &&
                   !verificationStatus.message?.includes("No face data") &&
                   !verificationStatus.message?.includes("5 ta rasm") && (
                    <p className="text-sm text-gray-600 mt-2">
                      Sizning tasdiqlash so'rovingiz admin tomonidan ko'rib chiqilmoqda.
                    </p>
                  )}
                  
                  {verificationStatus.message?.includes("5 ta rasm") && (
                    <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-800">
                        <strong>Eslatma:</strong> Sizda allaqachon 5 ta yuz rasmi bor. Yangi rasm qo'shish uchun admin bilan bog'laning.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Camera Modal */}
      {showCamera && (
        <FaceVerificationCamera
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(false)}
          requiredImages={3} // 3 ta rasm olish embedding sifatini yaxshilash uchun
        />
      )}
    </div>
  );
}

