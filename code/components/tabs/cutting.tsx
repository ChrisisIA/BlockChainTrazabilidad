"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface CuttingTabProps {
  data: any
  language: Language
}

export default function CuttingTab({ data, language }: CuttingTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"
  const sectionTitleClass = "text-emerald-400 font-semibold mb-4"

  const cuttingOrder = data?.tztotrazwebcort?.[0]
  const cuttingOps = data?.tztotrazwebcortoper || []

  if (!cuttingOrder && cuttingOps.length === 0) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noCuttingInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {cuttingOrder && (
        <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
          <h3 className={sectionTitleClass}>{t.cuttingProductionOrderSection}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className={`${subtextClass} text-sm mb-1`}>{t.cuttingProductionOrderNumber}</p>
              <p className={`${textClass} font-medium text-lg`}>{cuttingOrder.TNUMEORDECORT}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-sm mb-1`}>{t.fabricLyingID}</p>
              <p className={`${textClass} font-medium`}>{cuttingOrder.TNUMETEND}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-sm mb-1`}>{t.cuttingFinishingDate}</p>
              <p className={`${textClass} font-medium`}>
                {new Date(cuttingOrder.TFECHDESPCORT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
              </p>
            </div>
          </div>
        </div>
      )}

      {cuttingOps.length > 0 && (
        <div>
          <h3 className={sectionTitleClass}>{t.cuttingOperationsSection}</h3>
          <div className="space-y-3">
            {cuttingOps.map((op, idx) => (
              <div key={idx} className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationPersonnel}</p>
                    <p className={`${textClass} font-medium mb-3`}>({op.TCODIPERS}) {op.TNOMBPERS}</p>
                    <div className="flex">
                      <img
                        src={`http://app.nettalco.com.pe/php/foto.php?codigo=${op.TCODIPERS}`}
                        alt="Employee"
                        className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                        onError={(e) => {
                          e.currentTarget.src = "/placeholder-user.jpg"
                        }}
                      />
                    </div>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationDescription}</p>
                    <p className={`${textClass} font-medium`}>({op.TCODIOPER}) {op.TDESCOPER}</p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationDate}</p>
                    <p className={`${textClass} font-medium`}>
                      {new Date(op.TFECHLECT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                    </p>
                  </div>
                  <div>
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
