"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function AdminPanel() {
  const { user, isAuthenticated, isAdmin, logout, getAuthHeaders, loading: authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"verifications" | "rtsp">("verifications");
  const [pendingVerifications, setPendingVerifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [rtspCameras, setRtspCameras] = useState<any[]>([]);
  const [newCamera, setNewCamera] = useState({ name: "", url: "" });
  const [allCameras, setAllCameras] = useState<any[]>([]);
  const [viewingCamera, setViewingCamera] = useState<{ url: string; name: string; cameraId?: number } | null>(null);
  const [streamKey, setStreamKey] = useState(0); // For forcing stream reload

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
    
    // Check if user is admin
    if (!isAdmin) {
      router.push("/");
      return;
    }
    
    // Load data if user is authenticated admin
    loadPendingVerifications();
    loadRtspConfig();
    loadAllCameras();
  }, [isAuthenticated, isAdmin, authLoading, router]);

  const loadAllCameras = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAllCameras(data);
      }
    } catch (error) {
      console.error("Error loading cameras:", error);
    }
  };

  const loadPendingVerifications = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/verification/pending`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPendingVerifications(data);
      }
    } catch (error) {
      console.error("Error loading verifications:", error);
    }
  };

  const loadRtspConfig = async () => {
    try {
      // Load RTSP config from system config
      const configResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/config/rtsp/cameras`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (configResponse.ok) {
        const configData = await configResponse.json();
        setRtspCameras(configData.cameras || []);
      }

      // Also load all cameras from cameras API
      const camerasResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (camerasResponse.ok) {
        const camerasData = await camerasResponse.json();
        setAllCameras(camerasData);
      }
    } catch (error) {
      console.error("Error loading RTSP config:", error);
    }
  };

  const handleApprove = async (verificationId: number) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/verification/${verificationId}/approve`,
        {
          method: "POST",
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        await loadPendingVerifications();
        alert("Verification approved successfully");
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to approve");
      }
    } catch (error) {
      alert("Error approving verification");
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (verificationId: number) => {
    const notes = prompt("Rejection reason (optional):");
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/verification/${verificationId}/reject`,
        {
          method: "POST",
          headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ notes }),
        }
      );

      if (response.ok) {
        await loadPendingVerifications();
        alert("Verification rejected");
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to reject");
      }
    } catch (error) {
      alert("Error rejecting verification");
    } finally {
      setLoading(false);
    }
  };

  const handleAddCamera = async () => {
    if (!newCamera.name || !newCamera.url) {
      alert("Iltimos, barcha maydonlarni to'ldiring");
      return;
    }

    setLoading(true);
    try {
      const updatedCameras = [...rtspCameras, { ...newCamera, is_active: true }];
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/config/rtsp/cameras`,
        {
          method: "POST",
          headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify(updatedCameras),
        }
      );

      if (response.ok) {
        setNewCamera({ name: "", url: "" });
        await loadRtspConfig();
        alert("Kamera muvaffaqiyatli qo'shildi");
      } else {
        const error = await response.json();
        alert(error.detail || "Kamera qo'shishda xatolik");
      }
    } catch (error) {
      alert("Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCamera = async (index: number) => {
    if (!confirm("Bu kamerani o'chirishni xohlaysizmi?")) {
      return;
    }

    setLoading(true);
    try {
      const updatedCameras = rtspCameras.filter((_, i) => i !== index);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/config/rtsp/cameras`,
        {
          method: "POST",
          headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify(updatedCameras),
        }
      );

      if (response.ok) {
        await loadRtspConfig();
        alert("Kamera o'chirildi");
      } else {
        const error = await response.json();
        alert(error.detail || "Kamera o'chirishda xatolik");
      }
    } catch (error) {
      alert("Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCameraStatus = async (index: number) => {
    setLoading(true);
    try {
      const updatedCameras = [...rtspCameras];
      updatedCameras[index] = {
        ...updatedCameras[index],
        is_active: !updatedCameras[index].is_active,
      };
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/config/rtsp/cameras`,
        {
          method: "POST",
          headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify(updatedCameras),
        }
      );

      if (response.ok) {
        await loadRtspConfig();
      } else {
        const error = await response.json();
        alert(error.detail || "Holatni o'zgartirishda xatolik");
      }
    } catch (error) {
      alert("Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCameraActive = async (cameraId: number, isActive: boolean) => {
    setLoading(true);
    try {
      const cameraToUpdate = allCameras.find(c => c.id === cameraId);
      if (!cameraToUpdate) {
        alert("Camera not found in DB.");
        return;
      }
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/${cameraId}`,
        {
          method: "PUT",
          headers: {
            ...getAuthHeaders(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ ...cameraToUpdate, is_active: isActive }),
        }
      );
      if (response.ok) {
        await loadAllCameras();
        alert(`Camera ${cameraToUpdate.name} ${isActive ? "activated" : "deactivated"}.`);
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to update camera status.");
      }
    } catch (error) {
      alert("Error updating camera status.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCameraFromDB = async (cameraId: number, cameraName: string) => {
    if (!confirm(`Are you sure you want to delete camera "${cameraName}"?`)) {
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/${cameraId}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );
      if (response.ok) {
        await loadAllCameras();
        alert(`Camera "${cameraName}" deleted successfully.`);
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete camera.");
      }
    } catch (error) {
      alert("Error deleting camera.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh stream when viewing camera
  useEffect(() => {
    if (viewingCamera) {
      // Force stream reload every 5 seconds to prevent freezing
      const interval = setInterval(() => {
        setStreamKey(prev => prev + 1);
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [viewingCamera]);

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

  // Redirect if not authenticated or not admin
  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold text-gray-800">Admin Panel</h1>
              <Link href="/" className="text-blue-600 hover:text-blue-700">
                Dashboard
              </Link>
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

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab("verifications")}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === "verifications"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Face Verifications
              </button>
              <button
                onClick={() => setActiveTab("rtsp")}
                className={`px-6 py-4 text-sm font-medium ${
                  activeTab === "rtsp"
                    ? "border-b-2 border-blue-500 text-blue-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                RTSP Config
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === "verifications" && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Pending Face Verifications</h2>
                {pendingVerifications.length === 0 ? (
                  <p className="text-gray-500">No pending verifications</p>
                ) : (
                  <div className="space-y-4">
                    {pendingVerifications.map((verification) => (
                      <div
                        key={verification.id}
                        className="border border-gray-200 rounded-lg p-4 flex items-center justify-between"
                      >
                        <div className="flex items-center space-x-4">
                          <img
                            src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/static/${verification.image_path.split("/").pop()}`}
                            alt="Face"
                            className="w-24 h-24 object-cover rounded"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = "/placeholder.png";
                            }}
                          />
                          <div>
                            <p className="font-semibold">{verification.student_name}</p>
                            <p className="text-sm text-gray-500">
                              Student ID: {verification.student_id}
                            </p>
                            <p className="text-sm text-gray-500">
                              Confidence: {(verification.confidence * 100).toFixed(2)}%
                            </p>
                            {verification.camera && (
                              <p className="text-sm text-blue-600 font-medium">
                                📷 Kamera: {verification.camera.name}
                                {verification.camera.location && ` (${verification.camera.location})`}
                              </p>
                            )}
                            <p className="text-sm text-gray-500">
                              {new Date(verification.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleApprove(verification.id)}
                            disabled={loading}
                            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleReject(verification.id)}
                            disabled={loading}
                            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "rtsp" && (
              <div>
                <h2 className="text-2xl font-bold mb-4">RTSP Camera Configuration</h2>
                
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold mb-2">Add New RTSP Camera (Config)</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    RTSP kameralarni sozlash uchun (video worker uchun)
                  </p>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Camera Name"
                      value={newCamera.name}
                      onChange={(e) => setNewCamera({ ...newCamera, name: e.target.value })}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded"
                    />
                    <input
                      type="text"
                      placeholder="RTSP URL (rtsp://...)"
                      value={newCamera.url}
                      onChange={(e) => setNewCamera({ ...newCamera, url: e.target.value })}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded"
                    />
                    <button
                      onClick={handleAddCamera}
                      disabled={loading}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      Add
                    </button>
                  </div>
                </div>

                <div className="mb-6">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-xl font-semibold">RTSP Config Kameralar</h3>
                    <button
                      onClick={loadRtspConfig}
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Yangilash
                    </button>
                  </div>
                  <div className="space-y-2">
                    {rtspCameras.length === 0 ? (
                      <p className="text-gray-500">RTSP config'da kamera topilmadi</p>
                    ) : (
                      rtspCameras.map((camera, index) => (
                        <div
                          key={index}
                          className="border border-gray-200 rounded-lg p-4"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <p className="font-semibold">{camera.name || `Camera ${index + 1}`}</p>
                                <span
                                  className={`px-2 py-1 text-xs rounded ${
                                    camera.is_active !== false
                                      ? "bg-green-100 text-green-800"
                                      : "bg-gray-100 text-gray-800"
                                  }`}
                                >
                                  {camera.is_active !== false ? "Faol" : "Nofaol"}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-1">
                                <strong>URL:</strong> {camera.url || camera.rtsp_url || "N/A"}
                              </p>
                              {camera.location && (
                                <p className="text-sm text-gray-600 mb-1">
                                  <strong>Joylashuv:</strong> {camera.location}
                                </p>
                              )}
                            </div>
                            <div className="flex space-x-2 ml-4">
                              <button
                                onClick={() => {
                                  const cameraUrl = camera.url || camera.rtsp_url;
                                  if (cameraUrl) {
                                    // For RTSP config cameras, we don't have camera ID
                                    setViewingCamera({ 
                                      url: cameraUrl, 
                                      name: camera.name || `Camera ${index + 1}`,
                                      cameraId: undefined
                                    });
                                  } else {
                                    alert("Kamera URL topilmadi");
                                  }
                                }}
                                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                                title="RTSP stream'ni ko'rish"
                              >
                                Ko'rish
                              </button>
                              <button
                                onClick={() => handleToggleCameraStatus(index)}
                                disabled={loading}
                                className={`px-3 py-1 text-xs rounded ${
                                  camera.is_active !== false
                                    ? "bg-yellow-600 text-white hover:bg-yellow-700"
                                    : "bg-green-600 text-white hover:bg-green-700"
                                } disabled:opacity-50`}
                              >
                                {camera.is_active !== false ? "Nofaol qilish" : "Faollashtirish"}
                              </button>
                              <button
                                onClick={() => handleDeleteCamera(index)}
                                disabled={loading}
                                className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                              >
                                O'chirish
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-xl font-semibold">Barcha Database Kameralar</h3>
                    <button
                      onClick={loadAllCameras}
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Yangilash
                    </button>
                  </div>
                  {allCameras.length === 0 ? (
                    <p className="text-gray-500">Database'da kamera topilmadi</p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {allCameras.map((camera) => (
                        <div
                          key={camera.id}
                          className="border border-gray-200 rounded-lg p-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold">{camera.name}</h4>
                            <span
                              className={`px-2 py-1 text-xs rounded ${
                                camera.is_active
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {camera.is_active ? "Faol" : "Nofaol"}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-1">
                            <strong>Turi:</strong> {camera.camera_type === "rtsp" ? "RTSP" : "Laptop"}
                          </p>
                          {camera.location && (
                            <p className="text-sm text-gray-600 mb-1">
                              <strong>Joylashuv:</strong> {camera.location}
                            </p>
                          )}
                          {camera.rtsp_url && (
                            <p className="text-sm text-gray-600 mb-1 break-all">
                              <strong>RTSP URL:</strong> {camera.rtsp_url}
                            </p>
                          )}
                          {camera.camera_index !== null && (
                            <p className="text-sm text-gray-600 mb-1">
                              <strong>Index:</strong> {camera.camera_index}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 mt-2">
                            Yaratilgan: {new Date(camera.created_at).toLocaleDateString()}
                          </p>
                          <div className="mt-4 flex space-x-2">
                            <button
                              onClick={() => {
                                const cameraUrl = camera.rtsp_url || (camera.camera_type === "laptop" ? `Laptop Camera ${camera.camera_index}` : "");
                                setViewingCamera({ 
                                  url: cameraUrl, 
                                  name: camera.name,
                                  cameraId: camera.id
                                });
                                setStreamKey(prev => prev + 1); // Force reload
                              }}
                              disabled={!camera.is_active}
                              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                              title={camera.is_active ? "Kamera stream'ni ko'rish" : "Kamera nofaol, ko'rish mumkin emas"}
                            >
                              Ko'rish
                            </button>
                            <button
                              onClick={() => handleToggleCameraActive(camera.id, !camera.is_active)}
                              disabled={loading}
                              className={`px-3 py-1 text-sm rounded ${
                                camera.is_active
                                  ? "bg-yellow-500 hover:bg-yellow-600"
                                  : "bg-green-500 hover:bg-green-600"
                              } text-white disabled:opacity-50`}
                            >
                              {camera.is_active ? "Nofaol qilish" : "Faollashtirish"}
                            </button>
                            <button
                              onClick={() => handleDeleteCameraFromDB(camera.id, camera.name)}
                              disabled={loading}
                              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                            >
                              O'chirish
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>
        </div>
      </main>

      {/* RTSP Stream Viewer Modal */}
      {viewingCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Kamera Ko'rish: {viewingCamera.name}</h2>
              <button
                onClick={() => setViewingCamera(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>URL:</strong> {viewingCamera.url}
              </p>
              <div className="flex space-x-2 mb-4">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(viewingCamera.url);
                    alert("URL clipboard'ga nusxalandi!");
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  URL ni nusxalash
                </button>
                <button
                  onClick={() => {
                    // Try to open in VLC or default player
                    window.open(viewingCamera.url, '_blank');
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Tashqi o'yinchi'da ochish
                </button>
              </div>
            </div>

            {/* Video Stream */}
            <div className="bg-black rounded-lg p-4 mb-4 flex justify-center items-center min-h-[400px] relative">
              {(() => {
                // Debug: log camera info
                console.log("Viewing camera:", viewingCamera);
                
                if (viewingCamera.cameraId) {
                  // Database camera with ID
                  const streamUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/${viewingCamera.cameraId}/stream?t=${Date.now()}&key=${streamKey}`;
                  return (
                    <img
                      key={`camera-${viewingCamera.cameraId}-${streamKey}`}
                      src={streamUrl}
                      alt="Camera Stream"
                      className="max-w-full max-h-[600px] object-contain"
                      style={{ display: 'block' }}
                      onLoad={() => {
                        console.log("Stream loaded successfully");
                      }}
                      onError={(e) => {
                        console.error("Stream error:", e);
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        // Remove existing error div if any
                        const existingError = target.parentElement?.querySelector('.stream-error');
                        if (existingError) {
                          existingError.remove();
                        }
                        const errorDiv = document.createElement("div");
                        errorDiv.className = "stream-error text-white text-center p-4";
                        errorDiv.innerHTML = `
                          <p class="text-red-400 mb-2">Stream yuklanmadi</p>
                          <p class="text-sm text-gray-400 mb-2">Kamerani tekshiring yoki qayta urinib ko'ring</p>
                          <button onclick="window.location.reload()" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mt-2">
                            Qayta yuklash
                          </button>
                        `;
                        target.parentElement?.appendChild(errorDiv);
                      }}
                    />
                  );
                } else if (viewingCamera.url && (viewingCamera.url.startsWith('rtsp://') || viewingCamera.url.startsWith('http://') || viewingCamera.url.startsWith('https://'))) {
                  // RTSP Config camera without ID - use RTSP stream endpoint
                  const streamUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cameras/stream/rtsp?rtsp_url=${encodeURIComponent(viewingCamera.url)}&t=${Date.now()}&key=${streamKey}`;
                  return (
                    <img
                      key={`rtsp-${streamKey}`}
                      src={streamUrl}
                      alt="RTSP Stream"
                      className="max-w-full max-h-[600px] object-contain"
                      style={{ display: 'block' }}
                      onLoad={() => {
                        console.log("RTSP Stream loaded successfully");
                      }}
                      onError={(e) => {
                        console.error("Stream error:", e);
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        // Remove existing error div if any
                        const existingError = target.parentElement?.querySelector('.stream-error');
                        if (existingError) {
                          existingError.remove();
                        }
                        const errorDiv = document.createElement("div");
                        errorDiv.className = "stream-error text-white text-center p-4";
                        errorDiv.innerHTML = `
                          <p class="text-red-400 mb-2">Stream yuklanmadi</p>
                          <p class="text-sm text-gray-400 mb-2">RTSP kamera ulanmadi. URL'ni tekshiring yoki tashqi o'yinchi'da ochib ko'ring</p>
                          <p class="text-xs text-gray-500 mb-2">URL: ${viewingCamera.url}</p>
                          <button onclick="window.location.reload()" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mt-2">
                            Qayta yuklash
                          </button>
                        `;
                        target.parentElement?.appendChild(errorDiv);
                      }}
                    />
                  );
                } else {
                  // No valid camera info
                  return (
                    <div className="text-white text-center p-4">
                      <p className="text-yellow-400 mb-2">Stream ko'rsatish uchun kamera ma'lumotlari yetarli emas</p>
                      <p className="text-sm text-gray-400 mb-4">
                        {viewingCamera.url ? (
                          <>URL: {viewingCamera.url}<br />Tashqi o'yinchi'da ochib ko'ring</>
                        ) : (
                          "Kamerani qayta tanlang"
                        )}
                      </p>
                      {viewingCamera.url && (
                        <button
                          onClick={() => {
                            window.open(viewingCamera.url, '_blank');
                          }}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Tashqi o'yinchi'da ochish
                        </button>
                      )}
                    </div>
                  );
                }
              })()}
              
              {/* Reload button */}
              <button
                onClick={() => {
                  setStreamKey(prev => prev + 1);
                }}
                className="absolute top-2 right-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                title="Stream'ni qayta yuklash"
              >
                🔄
              </button>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setViewingCamera(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Yopish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

