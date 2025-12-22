"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface GarmentInfoTabProps {
  data: any
  language: Language
}

export default function GarmentInfoTab({ data, language }: GarmentInfoTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const sectionTitleClass = "text-lg font-semibold text-emerald-400 mb-4"
  const labelClass = `${subtextClass} text-sm mb-1`
  const valueClass = `${textClass} font-medium`

  const info = data?.tztotrazwebinfo?.[0]

  if (!info) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noGarmentInfo}</p>
      </div>
    )
  }

  const InfoBox = ({ label, value }: { label: string; value: any }) => (
    <div className={`${cardBgClass} rounded-lg p-4`}>
      <p className={labelClass}>{label}</p>
      <p className={valueClass}>{value || "N/A"}</p>
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Client Information Section */}
      <div>
        <h3 className={sectionTitleClass}>{t.clientInformation}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`${cardBgClass} rounded-lg p-6`}>
            <div className="space-y-4">
              <div>
                <p className={labelClass}>{t.clientName}</p>
                <p className={`${valueClass} text-xl`}>{info.TNOMBCLIE || "N/A"}</p>
              </div>
              <div>
                <p className={labelClass}>{t.clientCode}</p>
                <p className={`${subtextClass} text-sm`}>{info.TCODICLIE || "N/A"}</p>
              </div>
            </div>
          </div>
          <div className={`${cardBgClass} rounded-lg p-4 flex items-center justify-center min-h-[180px] md:col-span-2`}>
            <div className="text-center w-full">
              <img
                src={`/logos/logo_${info.TCODICLIE}.png`}
                alt="Client Logo"
                className="w-full h-auto max-h-[150px] object-contain mx-auto mb-2"
                onError={(e) => {
                  // Fallback to a placeholder image if the specific logo doesn't exist
                  e.currentTarget.src = "/placeholder-logo.png"
                }}
              />
              <p className={`${subtextClass} text-xs`}>{t.clientLogo}</p>
            </div>
          </div>
        </div>
      </div>

      {/* SKU Section */}
      <div>
        <h3 className={sectionTitleClass}>{t.sku}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <InfoBox label={t.clientStyle} value={info.TCODIESTICLIE} />
          <InfoBox label={t.clientStyleVersion} value={info.TNUMEVERSCLIE} />
          <InfoBox label={t.color} value={`(${info.TCODIETIQCLIEXEDI || ""}) ${info.TCODIETIQCLIE || ""}`.trim()} />
          <InfoBox label={t.size} value={info.TCODITALL} />
          <InfoBox label={t.nettalcoStyleId} value={info.TCODIESTINETT} />
          <InfoBox label={t.nettalcoStyleVersion} value={info.TNUMEVERSESTINETT} />
          <div className={`${cardBgClass} rounded-lg p-4 md:col-span-2 lg:col-span-2`}>
            <p className={labelClass}>{t.garmentDescription}</p>
            <p className={valueClass}>{info.TDESCPREN || "N/A"}</p>
          </div>
        </div>
        {/* Garment Image - Centered */}
        <div className="flex justify-center mt-4">
          <div className={`${cardBgClass} rounded-lg p-4 flex items-center justify-center min-h-[250px] w-full md:w-2/3 lg:w-1/2`}>
            <div className="text-center w-full">
              <img
                src={`http://app.nettalco.com.pe/php/fotoestinett_jpg.php?codiestinett=${info.TCODIESTINETT}`}
                alt="Garment"
                className="w-full h-auto max-h-[400px] object-contain mx-auto mb-2"
                onError={(e) => {
                  // Fallback to a placeholder image if the garment image doesn't exist
                  e.currentTarget.src = "/garment-image.jpg"
                }}
              />
              <p className={`${subtextClass} text-xs`}>{t.garmentImage}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Garment Attributes Section */}
      <div>
        <h3 className={sectionTitleClass}>{t.garmentAttributes}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InfoBox label={t.garmentType} value={`(${info.TTIPOPREN || ""}) ${info.TDESCTIPOPREN || ""}`.trim()} />
          <InfoBox label={t.program} value={`(${info.TCODIPROG || ""}) ${info.TDESCPROG || ""}`.trim()} />
          <InfoBox label={t.measurementGroup} value={`(${info.TGRUPMEDI || ""}) ${info.TDESCGRUPMEDI || ""}`.trim()} />
          <InfoBox label={t.ageStyle} value={`(${info.TINDIEDAD || ""}) ${info.TDESCEDAD || ""}`.trim()} />
          <InfoBox
            label={t.genderStyle}
            value={`(${info.TINDIGENE || ""}) ${info.TDESCGENE || ""} (${info.TGENDER || ""})`.trim()}
          />
        </div>
      </div>

      {/* Others Section */}
      <div>
        <h3 className={sectionTitleClass}>{t.others}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InfoBox label={t.quality} value={`(${info.TCLASIFIC || ""}) ${info.TDESCCLASPREN || ""}`.trim()} />
          <InfoBox label={t.currentLocation} value={info.TDESCUBIC} />
          <InfoBox label={t.channelId} value={info.TDESCGRUPFUPC} />
          <InfoBox
            label={t.directBusinessGarment}
            value={info.TDIREBUSI === "S" || info.TDIREBUSI === "Y" ? t.yes : t.no}
          />
        </div>
      </div>
    </div>
  )
}
