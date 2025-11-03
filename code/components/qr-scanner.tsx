"use client"

import { useEffect, useRef, useState } from "react"
import { X, AlertCircle } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"

interface QRScannerProps {
  onDetected: (hash: string) => void
  onClose: () => void
}

export default function QRScanner({ onDetected, onClose }: QRScannerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [isCameraSupported, setIsCameraSupported] = useState(true)
  const { theme, language } = useTheme()
  const t = translations[language]
  const streamRef = useRef<MediaStream | null>(null)
  const scanningRef = useRef(true)

  const isDark = theme === "dark"

  const checkCameraSupport = () => {
    return !!(typeof navigator !== "undefined" && navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  }

  const decodeQRCode = async (imageData: ImageData): Promise<string | null> => {
    try {
      // Dynamic import of jsqr
      const jsQR = (await import("jsqr")).default

      const code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
      })

      if (code) {
        console.log("[v0] QR Code detected:", code.data)
        return code.data
      }
      return null
    } catch (err) {
      console.error("[v0] jsQR error:", err)
      return null
    }
  }

  useEffect(() => {
    if (!checkCameraSupport()) {
      setIsCameraSupported(false)
      setError(t.cameraNotSupported)
      return
    }

    const startCamera = async () => {
      try {
        setError(null)

        const constraints = {
          video: {
            facingMode: "environment",
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        }

        const stream = await navigator.mediaDevices.getUserMedia(constraints)
        streamRef.current = stream

        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.onloadedmetadata = () => {
            setIsScanning(true)
            scanningRef.current = true
            scanQRCode()
          }
        }
      } catch (err) {
        if (err instanceof Error) {
          if (err.name === "NotAllowedError") {
            setError(t.cameraPermissionDenied)
          } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
            setError(t.cameraNotSupported)
          } else if (err.name === "NotReadableError") {
            setError(t.cameraNotAvailable)
          } else {
            setError(t.cameraNotAvailable)
          }
        } else {
          setError(t.cameraNotAvailable)
        }
        setIsScanning(false)
      }
    }

    startCamera()

    return () => {
      scanningRef.current = false
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
    }
  }, [t.cameraPermissionDenied, t.cameraNotSupported, t.cameraNotAvailable])

  const scanQRCode = async () => {
    const video = videoRef.current
    const canvas = canvasRef.current

    if (!video || !canvas || !scanningRef.current) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    try {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      if (canvas.width === 0 || canvas.height === 0) {
        if (scanningRef.current) {
          requestAnimationFrame(scanQRCode)
        }
        return
      }

      // Draw video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      // Get image data
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)

      // Detect QR code
      const code = await decodeQRCode(imageData)

      if (code) {
        console.log("[v0] QR Code detected successfully:", code)
        scanningRef.current = false
        setIsScanning(false)
        onDetected(code)
        return
      }
    } catch (err) {
      console.error("[v0] Scan error:", err)
    }

    if (scanningRef.current) {
      requestAnimationFrame(scanQRCode)
    }
  }

  if (!isCameraSupported) {
    return (
      <div
        className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${isDark ? "bg-black/80" : "bg-black/50"}`}
      >
        <div className={`w-full max-w-md rounded-xl overflow-hidden ${isDark ? "bg-slate-800" : "bg-white"}`}>
          <div
            className={`flex items-center justify-between p-4 border-b ${
              isDark ? "border-slate-700 bg-slate-900" : "border-slate-200 bg-slate-50"
            }`}
          >
            <h3 className={`text-lg font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{t.qrScanner}</h3>
            <button
              onClick={onClose}
              className={`p-1 rounded-lg transition-colors ${
                isDark ? "hover:bg-slate-700 text-slate-400" : "hover:bg-slate-200 text-slate-600"
              }`}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className={`p-6 text-center ${isDark ? "bg-slate-800" : "bg-white"}`}>
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
            <p className={`${isDark ? "text-slate-300" : "text-slate-600"} mb-4`}>{error}</p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors"
            >
              {t.closeCamera}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${isDark ? "bg-black/80" : "bg-black/50"}`}
    >
      <div className={`w-full max-w-md rounded-xl overflow-hidden ${isDark ? "bg-slate-800" : "bg-white"}`}>
        <div
          className={`flex items-center justify-between p-4 border-b ${
            isDark ? "border-slate-700 bg-slate-900" : "border-slate-200 bg-slate-50"
          }`}
        >
          <h3 className={`text-lg font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{t.qrScanner}</h3>
          <button
            onClick={onClose}
            className={`p-1 rounded-lg transition-colors ${
              isDark ? "hover:bg-slate-700 text-slate-400" : "hover:bg-slate-200 text-slate-600"
            }`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="relative bg-black aspect-square overflow-hidden">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
          <canvas ref={canvasRef} className="hidden" />

          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-64 h-64 border-2 border-emerald-500 rounded-lg shadow-lg shadow-emerald-500/50" />
          </div>

          <div className="absolute top-4 left-4 right-4 flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-white text-sm font-medium">{t.scanningQR}</span>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 border-t border-red-500/30 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className={`p-4 text-center ${isDark ? "bg-slate-700 text-slate-300" : "bg-slate-100 text-slate-600"}`}>
          <p className="text-sm">{t.qrNotDetected}</p>
        </div>
      </div>
    </div>
  )
}
