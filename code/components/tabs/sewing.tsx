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
                <p className={`${subtextClass} text-sm mb-1`}>{t.garmentClassificationEmployee}</p>
                <p className={`${textClass} font-medium mb-3`}>({sewingOrder.TCODIPERSCLAS}) {sewingOrder.TNOMBPERSCLAS}</p>
                <div className="flex">
                  <img
                    src={`http://app.nettalco.com.pe/php/foto.php?codigo=${sewingOrder.TCODIPERSCLAS}`}
                    alt="Employee"
                    className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder-user.jpg"
                    }}
                  />
                </div>
              </div>
              <div>
                <p className={`${subtextClass} text-sm mb-1`}>{t.garmentClassificationDate}</p>
                <p className={`${textClass} font-medium`}>
                  {new Date(sewingOrder.TFECHCLAS).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
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
                <p className={`${textClass} font-medium mb-3`}>({sewingOrder.TCODIPERSSUPE}) {sewingOrder.TNOMBPERSSUPE}</p>
                <div className="flex">
                  <img
                    src={`http://app.nettalco.com.pe/php/foto.php?codigo=${sewingOrder.TCODIPERSSUPE}`}
                    alt="Employee"
                    className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder-user.jpg"
                    }}
                  />
                </div>
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
          <p className={`${sectionTitleClass}`}>{t.sewingOperators}</p>
          <div className="space-y-3">
            {sewingOps.map((op, idx) => (
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
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationCode}</p>
                    <p className={`${textClass} font-medium`}>{op.TNUMEOPERESPE} ({op.TCODIOPERESPEVARISECU	})</p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.ticketsNumber}</p>
                    <p className={`${textClass} font-medium`}>{op.TCODITICK}</p>
                  </div>
                  <div>
                    <p className={`${subtextClass} text-sm mb-1`}>{t.operationDate}</p>
                    <p className={`${textClass} font-medium`}>
                      {new Date(op.TFECHLECT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                    </p>
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
