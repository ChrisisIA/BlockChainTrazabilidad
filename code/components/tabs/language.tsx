"use client"

import { useTheme } from "@/lib/theme-context"
import { translations, type Language } from "@/lib/i18n"

interface LanguageTabProps {
  language: Language
}

export default function LanguageTab({ language }: LanguageTabProps) {
  const { theme, setLanguage } = useTheme()
  const t = translations[language]
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-emerald-400 mb-4">{t.selectLanguage}</h3>
        <p className={`${subtextClass} mb-6`}>{t.languageDescription}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => setLanguage("en")}
          className={`p-6 rounded-lg border-2 transition-all ${
            language === "en" ? "border-emerald-500 bg-emerald-500/10" : `border-slate-300 ${cardBgClass}`
          }`}
        >
          <div className="text-3xl mb-3">🇺🇸</div>
          <p className={`${textClass} font-semibold text-lg`}>{t.english}</p>
          <p className={`${subtextClass} text-sm mt-2`}>English</p>
        </button>

        <button
          onClick={() => setLanguage("es")}
          className={`p-6 rounded-lg border-2 transition-all ${
            language === "es" ? "border-emerald-500 bg-emerald-500/10" : `border-slate-300 ${cardBgClass}`
          }`}
        >
          <div className="text-3xl mb-3">🇪🇸</div>
          <p className={`${textClass} font-semibold text-lg`}>{t.spanish}</p>
          <p className={`${subtextClass} text-sm mt-2`}>Español</p>
        </button>
      </div>
    </div>
  )
}
