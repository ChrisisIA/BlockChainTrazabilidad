"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface KnittingTabProps {
  data: any
  language: Language
}

function getBooleanText(val: string | number | undefined, language: Language): string {
  const t = translations[language]
  if (!val) return "-"
  const strVal = String(val).trim()
  return strVal === "1" ? t.yes : strVal === "0" ? t.no : "-"
}

function getFabricType(val: string | number | undefined, language: Language): string {
  const t = translations[language]
  if (!val) return "-"
  const strVal = String(val).trim()
  return strVal === "1" ? t.mainFabric : strVal === "0" ? t.complement : "-"
}

export default function KnittingTab({ data, language }: KnittingTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const sectionHeaderClass = isDark ? "text-emerald-300" : "text-emerald-600"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"

  const allKnittings = data?.tztotrazwebteje || []

  // Remove duplicates based on TORDETEJE and TNUMEOB combination
  const uniqueKnittings = allKnittings.filter((knit: any, index: number, self: any[]) => {
    return index === self.findIndex((k: any) => (
      k.TORDETEJE === knit.TORDETEJE && k.TNUMEOB === knit.TNUMEOB
    ))
  })

  // Sort knittings to show main fabric (TTELAPRIN = "1") first, then complements (TTELAPRIN = "0")
  const knittings = [...uniqueKnittings].sort((a: any, b: any) => {
    const aIsMain = String(a.TTELAPRIN).trim() === "1"
    const bIsMain = String(b.TTELAPRIN).trim() === "1"
    if (aIsMain && !bIsMain) return -1
    if (!aIsMain && bIsMain) return 1
    return 0
  })

  if (knittings.length === 0) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noKnittingInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <p className={`${subtextClass} text-sm`}>
        {t.productionOrders}: <span className="text-emerald-400 font-semibold">{knittings.length}</span>
      </p>

      {knittings.map((knit, idx) => (
        <div key={idx} className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
          <h3 className={`${sectionHeaderClass} font-semibold mb-4`}>
            {t.productionOrderNo}: {knit.TORDETEJE}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.productionOrderNo}</p>
              <p className={textClass}>{knit.TORDETEJE}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.productionRequestNo}</p>
              <p className={textClass}>{knit.TORDETEJE}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.totalWeight}</p>
              <p className={textClass}>{knit.TKILOCRUD?.toFixed(2) || "-"} kg</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.dyeingProductionOrderAttended}</p>
              <p className={textClass}>{knit.TNUMEOB || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoRawFabricId}</p>
              <p className={textClass}>{knit.TREDUCRUD || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabric}</p>
              <p className={textClass}>
                ({knit.TCODITELA}) {knit.TDESCTELA}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.gauge}</p>
              <p className={textClass}>{knit.TNUMEGALG || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.knittingItemType}</p>
              <p className={textClass}>{knit.TDESCTIPOARTI}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.coloredThread}</p>
              <p className={textClass}>{getBooleanText(knit.THILOCOLO, language)}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.knittingType}</p>
              <p className={textClass}>
                ({knit.TTIPOTEJI}) {knit.TDESCTIPOTEJI}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.knittingMachineType}</p>
              <p className={textClass}>
                ({knit.TTIPOMAQUTEJE}) {knit.TDESCTIPOMAQUTEJE}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.rawThreadType}</p>
              <p className={textClass}>
                ({knit.TCODIMATEPRIM}) {knit.TDESCCODIMATEPRIM}
              </p>
              <p className={textClass}>
                ({knit.TMATEPRIM}) {knit.TDESCMATEPRIM}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
