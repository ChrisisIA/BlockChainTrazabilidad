"use client"

import { X } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"

interface ScannerSelectorProps {
  onSelectQR: () => void
  onSelectBarcode: () => void
  onClose: () => void
}

export default function ScannerSelector({ onSelectQR, onSelectBarcode, onClose }: ScannerSelectorProps) {
  const { theme, language } = useTheme()
  const t = translations[language]
  const isDark = theme === "dark"

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${isDark ? "bg-black/80" : "bg-black/50"}`}
    >
      <div className={`w-full max-w-md rounded-xl overflow-hidden ${isDark ? "bg-slate-800" : "bg-white"}`}>
        {/* Header */}
        <div
          className={`flex items-center justify-between p-4 border-b ${
            isDark ? "border-slate-700 bg-slate-900" : "border-slate-200 bg-slate-50"
          }`}
        >
          <h3 className={`text-lg font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>{t.chooseScanner}</h3>
          <button
            onClick={onClose}
            className={`p-1 rounded-lg transition-colors ${
              isDark ? "hover:bg-slate-700 text-slate-400" : "hover:bg-slate-200 text-slate-600"
            }`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Options */}
        <div className={`p-6 space-y-4 ${isDark ? "bg-slate-800" : "bg-white"}`}>
          {/* QR Code Option */}
          <button
            onClick={onSelectQR}
            className={`w-full p-6 rounded-lg border-2 transition-all text-left ${
              isDark
                ? "border-slate-600 hover:border-emerald-500 hover:bg-slate-700"
                : "border-slate-300 hover:border-emerald-500 hover:bg-slate-50"
            }`}
          >
            <div className="text-3xl mb-3">📱</div>
            <h4 className={`font-semibold text-lg ${isDark ? "text-white" : "text-slate-900"}`}>{t.scanQRCode}</h4>
            <p className={`text-sm mt-2 ${isDark ? "text-slate-400" : "text-slate-600"}`}>{t.scanQRDesc}</p>
          </button>

          {/* Barcode Option */}
          <button
            onClick={onSelectBarcode}
            className={`w-full p-6 rounded-lg border-2 transition-all text-left ${
              isDark
                ? "border-slate-600 hover:border-emerald-500 hover:bg-slate-700"
                : "border-slate-300 hover:border-emerald-500 hover:bg-slate-50"
            }`}
          >
            <div className="text-3xl mb-3">📊</div>
            <h4 className={`font-semibold text-lg ${isDark ? "text-white" : "text-slate-900"}`}>{t.scanBarcode}</h4>
            <p className={`text-sm mt-2 ${isDark ? "text-slate-400" : "text-slate-600"}`}>{t.scanBarcodeDesc}</p>
          </button>
        </div>
      </div>
    </div>
  )
}
