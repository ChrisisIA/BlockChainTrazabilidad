"use client"

import { translations, type Language } from "@/lib/i18n"
import { useTheme } from "@/lib/theme-context"

interface DyeingTabProps {
  data: any
  language: Language
}

function extractValue(str: string | number | undefined): string {
  if (!str) return "-"
  const strVal = String(str)
  const firstPart = strVal.split(".")[0]
  return firstPart || "-"
}

function getBooleanText(val: string | number | undefined, language: Language): string {
  const t = translations[language]
  if (!val) return "-"
  const strVal = String(val).trim()
  return strVal === "1" ? t.yes : strVal === "0" ? t.no : "-"
}

export default function DyeingTab({ data, language }: DyeingTabProps) {
  const t = translations[language]
  const { theme } = useTheme()
  const isDark = theme === "dark"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-700/50" : "bg-slate-100"
  const innerCardBgClass = isDark ? "bg-slate-800/50" : "bg-slate-200"
  const sectionHeaderClass = isDark ? "text-emerald-300" : "text-emerald-600"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const borderClass = isDark ? "border-slate-600" : "border-slate-300"

  const allDyeings = data?.tztotrazwebtint || []

  // Filter main fabric (the one with TPEDISGT value)
  const mainOrder = allDyeings.find((dye: any) => dye.TPEDISGT && String(dye.TPEDISGT).trim() !== "")

  // Sort dyeings to show main fabric first, then others
  const dyeings = [...allDyeings].sort((a: any, b: any) => {
    const aHasPedisgt = a.TPEDISGT && String(a.TPEDISGT).trim() !== ""
    const bHasPedisgt = b.TPEDISGT && String(b.TPEDISGT).trim() !== ""
    if (aHasPedisgt && !bHasPedisgt) return -1
    if (!aHasPedisgt && bHasPedisgt) return 1
    return 0
  })

  if (dyeings.length === 0) {
    return (
      <div className="text-center py-8">
        <p className={subtextClass}>{t.noDyeingInfo}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Fabric Production Order Section */}
      {mainOrder && (
        <div className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
          <h3 className={`${sectionHeaderClass} font-semibold mb-4`}>{t.mainFabricProductionOrder}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.productionOrderNo}</p>
              <p className={textClass}>{mainOrder.TNUMEOB}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.productionRequestNo}</p>
              <p className={textClass}>{extractValue(mainOrder.TPEDISGT)}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.dispatchUnitNo}</p>
              <p className={textClass}>{mainOrder.TNUMEUD || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.programmedWeight}</p>
              <p className={textClass}>{mainOrder.TKILOPROG?.toFixed(2) || "-"} kg</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFinishedFabricId}</p>
              <p className={textClass}>{mainOrder.TREDUACAB || "-"}</p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabric}</p>
              <p className={textClass}>
                ({mainOrder.TCODITELA}) {mainOrder.TDESCTELA}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabricColorType}</p>
              <p className={textClass}>
                ({mainOrder.TTIPOCOLN}) {mainOrder.TDESCTIPOCOLN}
              </p>
            </div>
            <div>
              <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabricColor}</p>
              <p className={textClass}>
                ({mainOrder.TNUMECOLN}) {mainOrder.TDESCCOLN}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Dyeing Orders Section */}
      {dyeings.map((dye, idx) => (
        <div key={idx} className={`${cardBgClass} rounded-lg p-4 border ${borderClass}`}>
          <h3 className={`${sectionHeaderClass} font-semibold mb-4`}>
            {t.productionOrderNo}: {dye.TNUMEOB}
          </h3>

          {/* Fabric Subsection */}
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.productionRequestNo}</p>
                <p className={textClass}>{extractValue(dye.TPEDISGT)}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dispatchUnitNo}</p>
                <p className={textClass}>{dye.TNUMEUD || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.programmedWeight}</p>
                <p className={textClass}>{dye.TKILOACAB || "-"}</p>
              </div>
            </div>
          </div>
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.fabricSection}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFinishedFabricId}</p>
                <p className={textClass}>{dye.TREDUACAB || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabric}</p>
                <p className={textClass}>
                  ({dye.TCODITELA}) {dye.TDESCTELA}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabricColorType}</p>
                <p className={textClass}>
                  ({dye.TTIPOCOLN}) {dye.TDESCTIPOCOLN}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.nettalcoFabricColor}</p>
                <p className={textClass}>
                  ({dye.TNUMECOLN}) {dye.TDESCCOLN}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricType}</p>
                <p className={textClass}>
                  ({dye.TTIPOTELA}) {dye.TDESCTIPOTELA}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.finishingFabricType}</p>
                <p className={textClass}>{dye.TTIPOACABTELA || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.coloredThread}</p>
                <p className={textClass}>{getBooleanText(dye.THILOCOLO, language)}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.antipilling}</p>
                <p className={textClass}>{getBooleanText(dye.TINDIANTIPILI, language)}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.garmentComponentNo}</p>
                <p className={textClass}>({dye.TNUMECOMP}) {dye.TDESCCOMP || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.garmentComponentType}</p>
                <p className={textClass}>({dye.TTIPOCOMP}) {dye.TDESCTIPOCOMP || "-"}</p>
              </div>
            </div>
          </div>

          {/* Fabric Dyeing Subsection */}
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.fabricDyeingSection}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineId}</p>
                <p className={textClass}>
                  ({dye.TMAQUTENI}) {dye.TNOMBMAQUTENI}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineModel}</p>
                <p className={textClass}>
                  {dye.TMODEMAQUTENI} ({dye.TFABRMAQUTENI})
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.productionOrderGroup}</p>
                <p className={textClass}>{extractValue(dye.TPEDISGT)}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dyeingSetNo}</p>
                <p className={textClass}>{dye.TPARTTINT || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dyeingRecipeNo}</p>
                <p className={textClass}>{dye.TCODIRECE || "-"}</p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dyeingStart}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHTENIINIC).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dyeingFinish}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHTENIFINA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
            </div>
          </div>

          {/* Fabric Cutting Post Dyeing Subsection */}
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.fabricCuttingPostDyeing}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineId}</p>
                <p className={textClass}>
                  ({dye.TMAQUCORT}) {dye.TNOMBMAQUCORT}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineModel}</p>
                <p className={textClass}>
                  {dye.TMODEMAQUCORT} ({dye.TFABRMAQUCORT})
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricCuttingStart}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHCORTINIC).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricCuttingFinish}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHCORTFINA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div className="md:col-span-2">
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricCuttingEmployee}</p>
                <p className={textClass}>
                  ({dye.TOPERCORTINIC}) {dye.TNOMBOPERCORTINIC}
                </p>
                <div className="flex mt-3">
                  <img
                    src={`http://app.nettalco.com.pe/php/foto.php?codigo=${dye.TOPERCORTINIC}`}
                    alt="Employee"
                    className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder-user.jpg"
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Fabric Drying Subsection */}
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.fabricDryingSection}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineId}</p>
                <p className={textClass}>
                  ({dye.TMAQUSECA}) {dye.TNOMBMAQUSECA}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineModel}</p>
                <p className={textClass}>
                  {dye.TMODEMAQUSECA} ({dye.TFABRMAQUSECA})
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricDryingStart}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHSECAINIC).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricDryingFinish}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHSECAFINA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div className="md:col-span-2">
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricDryingEmployee}</p>
                <p className={textClass}>
                  ({dye.TOPERSECAINIC}) {dye.TNOMBOPERSECAINIC}
                </p>
                <div className="flex mt-3">
                  <img
                    src={`http://app.nettalco.com.pe/php/foto.php?codigo=${dye.TOPERSECAINIC}`}
                    alt="Employee"
                    className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder-user.jpg"
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Fabric Finishing Subsection */}
          <div className="mb-6 pb-4 border-b border-emerald-500/30">
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.fabricFinishingSection}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineId}</p>
                <p className={textClass}>
                  ({dye.TMAQUACAB}) {dye.TNOMBMAQUACAB}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.machineModel}</p>
                <p className={textClass}>
                  {dye.TMODEMAQUACAB} ({dye.TFABRMAQUACAB})
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricFinishingStart}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHACABINIC).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricFinishingFinish}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHACABFINA).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div className="md:col-span-2">
                <p className={`${subtextClass} text-xs mb-1`}>{t.fabricFinishingEmployee}</p>
                <p className={textClass}>
                  ({dye.TOPERACABINIC}) {dye.TNOMBOPERACABINIC}
                </p>
                <div className="flex mt-3">
                  <img
                    src={`http://app.nettalco.com.pe/php/foto.php?codigo=${dye.TOPERACABINIC}`}
                    alt="Employee"
                    className="w-[150px] h-[150px] object-cover rounded-full border-2 border-emerald-400 ml-5"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder-user.jpg"
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Final Operations Subsection */}
          <div>
            <h4 className={`${sectionHeaderClass} font-medium mb-3 text-sm`}>{t.finalOperations}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.qualityControlDate}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHCALITINT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
              <div>
                <p className={`${subtextClass} text-xs mb-1`}>{t.dispatchDateToCutting}</p>
                <p className={textClass}>
                  {new Date(dye.TFECHDESPTINT).toLocaleString(language === "en" ? "en-US" : "es-ES")}
                </p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
