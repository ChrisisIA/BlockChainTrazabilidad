"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Copy, Download } from "lucide-react"
import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface RawDataTabProps {
  data: any
  endpoint: string
  language: Language
}

export default function RawDataTab({ data, endpoint, language }: RawDataTabProps) {
  const [copied, setCopied] = useState(false)
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-900" : "bg-slate-100"
  const textClass = isDark ? "text-slate-300" : "text-slate-700"
  const borderClass = isDark ? "border-slate-700" : "border-slate-300"

  const jsonString = JSON.stringify(data, null, 2)

  const copyJson = () => {
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadJson = () => {
    const element = document.createElement("a")
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(jsonString))
    element.setAttribute("download", "traceability-data.json")
    element.style.display = "none"
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <Button onClick={copyJson} className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2">
          <Copy className="w-4 h-4" />
          {copied ? t.copied : "Copy JSON"}
        </Button>
        <Button
          onClick={downloadJson}
          className={`${isDark ? "bg-slate-700 hover:bg-slate-600 text-slate-300" : "bg-slate-300 hover:bg-slate-400 text-slate-700"} flex items-center gap-2`}
        >
          <Download className="w-4 h-4" />
          {t.downloadJSON}
        </Button>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass} overflow-auto max-h-96`}>
        <pre className={`${textClass} text-xs font-mono whitespace-pre-wrap break-words`}>{jsonString}</pre>
      </div>

      <div className={`${isDark ? "bg-slate-700/50" : "bg-slate-100"} rounded-lg p-4 border ${borderClass}`}>
        <p className={`${subtextClass} text-sm mb-2`}>{t.endpointData}</p>
        <p className="text-emerald-400 text-xs font-mono break-all">{endpoint}</p>
      </div>
    </div>
  )
}
