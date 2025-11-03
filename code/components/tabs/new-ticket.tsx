"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations, type Language } from "@/lib/i18n"

interface NewTicketTabProps {
  language: Language
  onSearch: (hash: string) => void
  isLoading?: boolean
}

export default function NewTicketTab({ language, onSearch, isLoading = false }: NewTicketTabProps) {
  const [hash, setHash] = useState("")
  const { theme } = useTheme()
  const t = translations[language]
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const inputBgClass = isDark ? "bg-slate-700 border-slate-600 text-white" : "bg-white border-slate-300 text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (hash.trim()) {
      onSearch(hash.trim())
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-emerald-400 mb-4">{t.enterNewHash}</h3>
        <p className={`${subtextClass} mb-6`}>{t.newHashDescription}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <input
            type="text"
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            placeholder={t.enterHashPlaceholder}
            className={`w-full px-4 py-3 rounded-lg border ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
          />
        </div>

        <Button
          type="submit"
          disabled={!hash.trim() || isLoading}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center gap-2 py-3"
        >
          <Search className="w-4 h-4" />
          {isLoading ? t.searching : t.searchNewHash}
        </Button>
      </form>

      <div
        className={`${isDark ? "bg-slate-700/50 border-slate-600" : "bg-slate-100 border-slate-300"} rounded-lg p-4 border`}
      >
        <p className={`${subtextClass} text-sm`}>{t.searchDescription}</p>
      </div>
    </div>
  )
}
