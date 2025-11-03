"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface WarehouseTabProps {
  data: any
  language: Language
}

export default function WarehouseTab({ data, language }: WarehouseTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"
  const sectionTitleClass = "text-emerald-400 font-semibold mb-4"

  const warehouse = data?.tztotrazwebalma?.[0]

  if (!warehouse) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noWarehouseInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.cartonSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.clientCartonNumber}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.nettalcoCartonNumber}</p>
            <p className={`${textClass} font-medium text-lg`}>{warehouse.TNUMECAJA}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.cartonGarmentQuantity}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TCANTPREN}</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.purchaseOrderSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.orderNumber}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TPURCORDE}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.season}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TCODITEMP}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.destination}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TDESCDEST}</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.shippingSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.packingListNumber}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.invoiceNumber}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.gotsCertification}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.remissionGuideNumber}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.shippingID}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.receptionSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.cartonType}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TDESCTIPOCAJA}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.receptionDate}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(warehouse.TFECHRECEALMA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.receptionEmployee}</p>
            <p className={`${textClass} font-medium`}>{warehouse.TNOMBPERSRECEALMA}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
