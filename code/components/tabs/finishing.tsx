"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface FinishingTabProps {
  data: any
  language: Language
}

export default function FinishingTab({ data, language }: FinishingTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"
  const sectionTitleClass = "text-emerald-400 font-semibold mb-4"

  const finishing = data?.tztotrazwebacab?.[0]

  if (!finishing) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noFinishingInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.cartonWeightSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.nettalcoCartonNumber}</p>
            <p className={`${textClass} font-medium`}>{finishing.TNUMECAJA}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.weightCartonDate}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHPESA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.weightCartonEmployee}</p>
            <p className={`${textClass} font-medium mb-3`}>({finishing.TCODIPERSPESA}) {finishing.TNOMBPERSPESA}</p>
            <div className="flex">
              <img
                src={`http://app.nettalco.com.pe/php/foto.php?codigo=${finishing.TCODIPERSPESA}`}
                alt="Employee"
                className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-4"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder-user.jpg"
                }}
              />
            </div>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.grossWeight}</p>
            <p className={`${textClass} font-medium`}>
              {finishing.TPESOBRUT} {t.kg}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.netWeight}</p>
            <p className={`${textClass} font-medium`}>
              {finishing.TPESONETO} {t.kg}
            </p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.cartonPackingSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.cartonPackingEmployee}</p>
            <p className={`${textClass} font-medium mb-3`}>({finishing.TCODIPERSEMPA}) {finishing.TNOMBPERSEMPA}</p>
            <div className="flex">
              <img
                src={`http://app.nettalco.com.pe/php/foto.php?codigo=${finishing.TCODIPERSEMPA}`}
                alt="Employee"
                className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder-user.jpg"
                }}
              />
            </div>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.cartonPackingDate}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHEMPA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div> 
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.qualityAuditSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.qualityAuditEmployee}</p>
            <p className={`${textClass} font-medium mb-3`}>({finishing.TCODIPERSAUDI}) {finishing.TNOMBPERSAUDI}</p>
            <div className="flex">
              <img
                src={`http://app.nettalco.com.pe/php/foto.php?codigo=${finishing.TCODIPERSAUDI}`}
                alt="Employee"
                className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder-user.jpg"
                }}
              />
            </div>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.qualityAuditDate}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHAUDI).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.qualityBatch}</p>
            <p className={`${textClass} font-medium`}>{finishing.TLOTEAUDIESTA}</p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.garmentWasPartOfSampling}</p>
            <p className={`${textClass} font-medium`}>-</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.shelvingWarehouseSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.shelvingWarehouseReception}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHINGRESTA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.shelvingWarehouseCartonNumber}</p>
            <p className={`${textClass} font-medium`}>{finishing.TNUMECAJAESTA}</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.finishingGarmentProductionModuleSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.productionModuleDate}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHMODU).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.productionModuleID}</p>
            <p className={`${textClass} font-medium`}>{finishing.TCODIMODU}</p>
          </div>
        </div>
      </div>

      <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
        <h3 className={sectionTitleClass}>{t.finishingGarmentReceptionSection}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.finishingGarmentReceptionEmployee}</p>
            <p className={`${textClass} font-medium mb-3`}>({finishing.TCODIRECEBANDCOST}) {finishing.TNOMBRECEBANDCOST}</p>
            <div className="flex">
              <img
                src={`http://app.nettalco.com.pe/php/foto.php?codigo=${finishing.TCODIRECEBANDCOST}`}
                alt="Employee"
                className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder-user.jpg"
                }}
              />
            </div>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.finishingGarmentReception}</p>
            <p className={`${textClass} font-medium`}>
              {new Date(finishing.TFECHRECEBANDCOST).toLocaleString(language === "en" ? "en-US" : "es-ES")}
            </p>
          </div>
          <div>
            <p className={`${subtextClass} text-sm mb-1`}>{t.garmentType}</p>
            <p className={`${textClass} font-medium`}>{finishing.TDESCTIPOTICK}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
