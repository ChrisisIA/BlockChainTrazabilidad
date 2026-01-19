"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader2, Sun, Moon, Camera } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"
import QRScanner from "./qr-scanner"
import ScannerSelector from "./scanner-selector"
import BarcodeScanner from "./barcode-scanner"
import FilterPanel, { type FilterState } from "./filter-panel"
import ChatInterface from "./chat-interface"

interface HashInputProps {
  onSubmit: (hash: string) => void
  loading: boolean
  error: string | null
}

export default function HashInput({ onSubmit, loading, error }: HashInputProps) {
  const [tickbarr, setTickbarr] = useState("")
  const [showQRScanner, setShowQRScanner] = useState(false)
  const [showScannerSelector, setShowScannerSelector] = useState(false)
  const [showBarcodeScanner, setShowBarcodeScanner] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const [chatFilters, setChatFilters] = useState<FilterState | undefined>(undefined)
  const [externalFiltersForPanel, setExternalFiltersForPanel] = useState<Partial<FilterState> | undefined>(undefined)
  const { theme, toggleTheme, language, setLanguage } = useTheme()
  const t = translations[language]

  // Handler para filtros extraídos del chat (Chat → Filtros)
  const handleFiltersFromChat = (extractedFilters: FilterState, corrections?: Record<string, string>) => {
    // Merge: solo llenar campos vacíos del panel de filtros
    const mergedFilters: FilterState = {
      client: chatFilters?.client || extractedFilters.client || "",
      clientStyle: chatFilters?.clientStyle || extractedFilters.clientStyle || "",
      boxNumber: chatFilters?.boxNumber || extractedFilters.boxNumber || "",
      label: chatFilters?.label || extractedFilters.label || "",
      size: chatFilters?.size || extractedFilters.size || "",
      gender: chatFilters?.gender || extractedFilters.gender || "",
      age: chatFilters?.age || extractedFilters.age || "",
      garmentType: chatFilters?.garmentType || extractedFilters.garmentType || "",
    }

    setChatFilters(mergedFilters)
    // Enviar filtros externos al panel para actualización visual
    setExternalFiltersForPanel(extractedFilters)

    if (corrections && Object.keys(corrections).length > 0) {
      console.log("[SYNC] Correcciones aplicadas:", corrections)
    }
  }

  // Handler para filtros del panel (Filtros → Chat)
  const handleFiltersFromPanel = (filters: FilterState) => {
    setChatFilters(filters)
    // Limpiar filtros externos ya que el usuario editó manualmente
    setExternalFiltersForPanel(undefined)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tickbarr.trim()) return

    setLocalError(null)

    try {
      // First, call the tickbarr endpoint to get the hash
      const tickbarrResponse = await fetch("http://128.0.17.5:5000/get_hash", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ tickbarr: tickbarr.trim() }),
      })

      if (!tickbarrResponse.ok) {
        const errorData = await tickbarrResponse.json()
        throw new Error(errorData.error || "Tickbarr not found")
      }

      const tickbarrData = await tickbarrResponse.json()
      const hash = tickbarrData.hash

      if (!hash) {
        throw new Error("No hash returned from tickbarr endpoint")
      }

      // Then submit the hash to the parent component
      onSubmit(hash)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error fetching tickbarr data"
      setLocalError(message)
    }
  }

  const handleQRDetected = (detectedTickbarr: string) => {
    setTickbarr(detectedTickbarr)
    setShowQRScanner(false)
    // Auto-submit after QR detection
    setTimeout(() => {
      const formEvent = new Event("submit", { bubbles: true })
      const submitButton = document.querySelector("button[type='submit']") as HTMLButtonElement
      if (submitButton) {
        submitButton.click()
      }
    }, 100)
  }

  const handleBarcodeDetected = (detectedTickbarr: string) => {
    setTickbarr(detectedTickbarr)
    setShowBarcodeScanner(false)
    // Auto-submit after barcode detection
    setTimeout(() => {
      const formEvent = new Event("submit", { bubbles: true })
      const submitButton = document.querySelector("button[type='submit']") as HTMLButtonElement
      if (submitButton) {
        submitButton.click()
      }
    }, 100)
  }

  const isDark = theme === "dark"
  const bgClass = isDark
    ? "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
    : "bg-gradient-to-br from-slate-50 via-white to-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const inputBgClass = isDark
    ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400"
    : "bg-slate-100 border-slate-300 text-slate-900 placeholder-slate-500"

  const displayError = localError || error

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center px-4 py-6 md:py-12 ${bgClass}`}>
      <div className="w-full max-w-2xl lg:max-w-5xl xl:max-w-6xl">
        {/* Header with Theme Toggle and Language Selector */}
        <div className="flex justify-end gap-2 mb-4 md:mb-6">
          <button
            onClick={() => setLanguage(language === "en" ? "es" : "en")}
            className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              isDark
                ? "bg-slate-700 hover:bg-slate-600 text-slate-300"
                : "bg-slate-200 hover:bg-slate-300 text-slate-700"
            }`}
            title={language === "en" ? "Cambiar a Español" : "Switch to English"}
          >
            <span className="text-lg">{language === "en" ? "🇬🇧" : "🇪🇸"}</span>
            <span className="text-sm font-medium">{language === "en" ? "Language" : "Idioma"}</span>
          </button>
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-colors ${
              isDark
                ? "bg-slate-700 hover:bg-slate-600 text-yellow-400"
                : "bg-slate-200 hover:bg-slate-300 text-slate-700"
            }`}
            title={isDark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>

        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-2xl">⛓</span>
            </div>
            <h1 className={`text-3xl md:text-5xl font-bold ${textClass}`}>{t.title}</h1>
          </div>
          <p className={`${subtextClass} text-base md:text-lg`}>{t.subtitle}</p>
        </div>

        {/* Tickbarr Input Form */}
        <div className={`${cardBgClass} rounded-xl p-6 md:p-8 border shadow-xl`}>
          <h2 className={`text-xl md:text-2xl font-bold ${textClass} mb-6 text-center`}>{t.enterHash}</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Input
                  type="text"
                  placeholder={t.searchPlaceholder}
                  value={tickbarr}
                  onChange={(e) => setTickbarr(e.target.value)}
                  disabled={loading}
                  className={`w-full px-4 py-4 text-base ${inputBgClass} rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50`}
                />
              </div>
              <button
                type="button"
                onClick={() => setShowScannerSelector(true)}
                disabled={loading}
                className={`px-6 py-4 rounded-lg transition-colors flex items-center justify-center gap-2 font-semibold whitespace-nowrap ${
                  isDark
                    ? "bg-slate-700 hover:bg-slate-600 text-slate-300 disabled:opacity-50"
                    : "bg-slate-200 hover:bg-slate-300 text-slate-700 disabled:opacity-50"
                }`}
                title={t.scanQR}
              >
                <Camera className="w-5 h-5" />
                <span>{t.scanQR}</span>
              </button>
            </div>

            {displayError && (
              <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-400 text-sm">{displayError}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading || !tickbarr.trim()}
              className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {t.searching}
                </>
              ) : (
                t.search
              )}
            </Button>
          </form>

          <p className={`${subtextClass} text-sm mt-6 text-center`}>{t.searchDescription}</p>
        </div>

        {/* Filters and Chatbot Section */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Panel - Left Side */}
          <div className="lg:col-span-1">
            <FilterPanel
              language={language}
              onApplyFilters={handleFiltersFromPanel}
              externalFilters={externalFiltersForPanel}
            />
          </div>

          {/* Chat Interface - Right Side */}
          <div className="lg:col-span-3">
            <ChatInterface
              language={language}
              filters={chatFilters}
              onFiltersExtracted={handleFiltersFromChat}
            />
          </div>
        </div>
      </div>

      {showScannerSelector && (
        <ScannerSelector
          onSelectQR={() => {
            setShowScannerSelector(false)
            setShowQRScanner(true)
          }}
          onSelectBarcode={() => {
            setShowScannerSelector(false)
            setShowBarcodeScanner(true)
          }}
          onClose={() => setShowScannerSelector(false)}
        />
      )}
      {showQRScanner && <QRScanner onDetected={handleQRDetected} onClose={() => setShowQRScanner(false)} />}
      {showBarcodeScanner && (
        <BarcodeScanner onDetected={handleBarcodeDetected} onClose={() => setShowBarcodeScanner(false)} />
      )}
    </div>
  )
}
