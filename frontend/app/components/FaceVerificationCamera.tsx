"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import { FaceDetection } from "@mediapipe/face_detection";
import { Camera } from "@mediapipe/camera_utils";

interface FaceVerificationCameraProps {
  onCapture: (imageBlob: Blob) => void;
  onClose: () => void;
}

export default function FaceVerificationCamera({
  onCapture,
  onClose,
}: FaceVerificationCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [faceDistance, setFaceDistance] = useState<number | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const faceDetectionRef = useRef<FaceDetection | null>(null);
  const cameraRef = useRef<Camera | null>(null);

  // Initialize MediaPipe Face Detection
  useEffect(() => {
    if (!videoRef.current) return;

    const faceDetection = new FaceDetection({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
      },
    });

    faceDetection.setOptions({
      model: "short",
      minDetectionConfidence: 0.5,
    });

    faceDetection.onResults((results) => {
      if (results.detections && results.detections.length > 0) {
        const detection = results.detections[0];
        const bbox = detection.boundingBox;
        
        // Calculate face size ratio
        const faceWidth = bbox.width;
        const faceHeight = bbox.height;
        const faceArea = faceWidth * faceHeight;
        
        if (videoRef.current) {
          const videoWidth = videoRef.current.videoWidth;
          const videoHeight = videoRef.current.videoHeight;
          const frameArea = videoWidth * videoHeight;
          const faceRatio = faceArea / frameArea;
          
          // Face is close if it takes up more than 15% of frame
          const isClose = faceRatio > 0.15;
          const distance = faceRatio; // 0-1, higher = closer
          
          setFaceDetected(true);
          setFaceDistance(distance);
          
          // Draw on canvas
          if (canvasRef.current) {
            const ctx = canvasRef.current.getContext("2d");
            if (ctx && videoRef.current) {
              canvasRef.current.width = videoRef.current.videoWidth;
              canvasRef.current.height = videoRef.current.videoHeight;
              ctx.drawImage(videoRef.current, 0, 0);
              
              // Draw face box
              ctx.strokeStyle = isClose ? "#00ff00" : "#ffff00";
              ctx.lineWidth = 2;
              ctx.strokeRect(bbox.xCenter - bbox.width / 2, bbox.yCenter - bbox.height / 2, bbox.width, bbox.height);
              
              // Draw text
              ctx.fillStyle = isClose ? "#00ff00" : "#ffff00";
              ctx.font = "16px Arial";
              ctx.fillText(
                isClose ? "✅ Yuz yaqin! Capture qilish mumkin" : "⚠️ Yuzni yaqinlashtiring",
                10,
                30
              );
            }
          }
        }
      } else {
        setFaceDetected(false);
        setFaceDistance(null);
      }
    });

    faceDetectionRef.current = faceDetection;

    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Start camera
  const startCamera = useCallback(async () => {
    try {
      if (!videoRef.current || !faceDetectionRef.current) return;

      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current && faceDetectionRef.current) {
            await faceDetectionRef.current.send({ image: videoRef.current });
          }
        },
        width: 640,
        height: 480,
      });

      cameraRef.current = camera;
      await camera.start();
      setIsStreaming(true);
    } catch (error) {
      console.error("Error accessing camera:", error);
      alert("Kameraga kirishda xatolik. Iltimos, ruxsat bering.");
    }
  }, []);


  // Capture image when face is close
  const captureImage = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !faceDetected) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    setIsCapturing(true);

    // Draw current frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob(
      (blob) => {
        if (blob) {
          onCapture(blob);
          setIsCapturing(false);
        }
      },
      "image/jpeg",
      0.95
    );
  }, [faceDetected, onCapture]);

  // Auto-capture when face is close enough
  useEffect(() => {
    if (faceDetected && faceDistance !== null && faceDistance > 0.7 && !isCapturing) {
      const timer = setTimeout(() => {
        captureImage();
      }, 500); // Wait 500ms to ensure face is stable
      return () => clearTimeout(timer);
    }
  }, [faceDetected, faceDistance, isCapturing, captureImage]);

  // Start camera on mount
  useEffect(() => {
    startCamera();
  }, [startCamera]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Yuzni Tasdiqlash - Camera</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full rounded-lg"
            style={{ transform: "scaleX(-1)" }} // Mirror effect
          />
          <canvas ref={canvasRef} className="hidden" />
          
          {!isStreaming && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 rounded-lg">
              <div className="text-white text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                <p>Kamera yuklanmoqda...</p>
              </div>
            </div>
          )}

          {isStreaming && !faceDetected && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-lg">
              <div className="text-white text-center">
                <p className="text-lg mb-2">Yuzingizni kameraga qarating</p>
                <p className="text-sm">Yuzingiz aniq ko'rinishi kerak</p>
              </div>
            </div>
          )}

          {faceDetected && faceDistance !== null && (
            <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-4 py-2 rounded">
              {faceDistance > 0.7 ? (
                <p className="text-green-400">✅ Yuz yaqin! Capture qilinmoqda...</p>
              ) : (
                <p className="text-yellow-400">
                  ⚠️ Yuzni yaqinlashtiring ({Math.round(faceDistance * 100)}%)
                </p>
              )}
            </div>
          )}
        </div>

        <div className="mt-4 flex justify-center space-x-4">
          <button
            onClick={captureImage}
            disabled={!faceDetected || isCapturing}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCapturing ? "Capture qilinmoqda..." : "Capture"}
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Bekor qilish
          </button>
        </div>

        <p className="mt-4 text-sm text-gray-600 text-center">
          Yuzingizni kameraga yaqinlashtiring. Yuz aniq ko'ringanda avtomatik capture qilinadi.
        </p>
      </div>
    </div>
  );
}

