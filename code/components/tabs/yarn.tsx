"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface YarnTabProps {
  data: any
  language: Language
}

function extractYarnValue(str: string | number | undefined): string {
  if (!str) return "-"
  const strVal = String(str)
  const parts = strVal.split(".")
  if (parts[0]) return parts[0]
  return "-"
}

function getFabricType(val: string | number | undefined, language: Language): string {
  const t = translations[language]
  if (!val) return "-"
  const strVal = String(val).trim()
  return strVal === "1" ? t.mainFabric : strVal === "0" ? t.complement : "-"
}

export default function YarnTab({ data, language }: YarnTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const sectionHeaderClass = isDark ? "text-emerald-300" : "text-emerald-600"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"

  const yarns = data?.tztotrazwebhilo || []

  if (yarns.length === 0) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noYarnInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h3 className={`${sectionHeaderClass} font-semibold`}>{t.yarnOfTheGarment}</h3>

      {yarns.map((yarn, idx) => (
        <div key={idx} className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
          <div className="mb-4 pb-4 border-b border-emerald-500/30">
            <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoRawFabricId}</p>
            <p className={textClass}>
              {extractYarnValue(yarn.TREDUCRUD)} ({yarn.TTELAPRIN ? getFabricType(yarn.TTELAPRIN, language) : "-"})
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabric}</p>
              <p className={textClass}>
                ({yarn.TCODITELA}) {yarn.TDESCTELA}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.itemType}</p>
              <p className={textClass}>{yarn.TDESCTIPOARTI || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.mainYarnId}</p>
              <p className={textClass}>{extractYarnValue(yarn.TREDUHILOPRIN)}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.mainYarn}</p>
              <p className={textClass}>
                ({yarn.THILOPRIN}) {yarn.TDESCHILOPRIN}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.yarnBatch}</p>
              <p className={textClass}>
                {yarn.TLOTEHILA} / {yarn.TLOTENETT}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.mainYarnProvider}</p>
              <p className={textClass}>
                ({yarn.TPROVPRIN}) {yarn.TNOMBPROVPRIN}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
