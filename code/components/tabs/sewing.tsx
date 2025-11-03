"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface SewingTabProps {
  data: any
  language: Language
}

export default function SewingTab({ data, language }: SewingTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"
  const sectionTitleClass = "text-emerald-400 font-semibold mb-4"

  const sewingOrder = data?.tztotrazwebcost?.[0]
  const sewingOps = data?.tztotrazwebcostoper || []

  if (!sewingOrder && sewingOps.length === 0) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noSewingInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {sewingOrder && (
        <>
          <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
            <h3 className={sectionTitleClass}>{t.productionOrderSection}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingProductionOrder}</p>
                <p className={`${textClass} font-medium`}>
                  {sewingOrder.TORDECOST} - {sewingOrder.TNUMEPEDI} - {sewingOrder.TNUMECORR}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingPackageNumber}</p>
                <p className={`${textClass} font-medium`}>{sewingOrder.TNUMEPAQU}</p>
              </div>
            </div>
          </div>

          <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
            <h3 className={sectionTitleClass}>{t.garmentClassificationSection}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.garmentClassificationDate}</p>
                <p className={`${textClass} font-medium`}>
                  {new Date(sewingOrder.TFECHCLAS).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.garmentClassificationEmployee}</p>
                <p className={`${textClass} font-medium`}>{sewingOrder.TNOMBPERSCLAS}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingDispatchTrayID}</p>
                <p className={`${textClass} font-medium`}>{sewingOrder.TCODIBAND}</p>
              </div>
            </div>
          </div>

          <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
            <h3 className={sectionTitleClass}>{t.productionLineSection}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingProductionLine}</p>
                <p className={`${textClass} font-medium`}>Line #{sewingOrder.TNUMELINECOST}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingProductionPlant}</p>
                <p className={`${textClass} font-medium`}>{sewingOrder.TDESCPLANCOST}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingProductionLineSupervisor}</p>
                <p className={`${textClass} font-medium`}>{sewingOrder.TNOMBPERSSUPE}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.sewingReceptionDate}</p>
                <p className={`${textClass} font-medium`}>
                  {new Date(sewingOrder.TFECHDESPCORT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {sewingOps.length > 0 && (
        <div>
          <p className={`${sectionTitleClass}`}>{t.cuttingOperationsSection}</p>
          <div className="space-y-3">
            {sewingOps.map((op, idx) => (
              <div key={idx} className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationCode}</p>
                    <p className={`${textClass} font-medium`}>{op.TCODIOPER}</p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationDescription}</p>
                    <p className={`${textClass} font-medium`}>{op.TDESCOPER}</p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationDate}</p>
                    <p className={`${textClass} font-medium`}>
                      {new Date(op.TFECHLECT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                    </p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationPersonnel}</p>
                    <p className={`${textClass} font-medium`}>{op.TNOMBPERS}</p>
                  </div>
                  <div className="md:col-span-2">
                    <p className={`${subtextClass} text-sm mb-1`}>{t.ticketsNumber}</p>
                    <p className={`${textClass} font-medium`}>{op.TNUMETICK}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
