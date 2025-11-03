"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronLeft, Copy, ExternalLink, Sun, Moon } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"
import GarmentInfoTab from "./tabs/garment-info"
import WarehouseTab from "./tabs/warehouse"
import FinishingTab from "./tabs/finishing"
import SewingTab from "./tabs/sewing"
import CuttingTab from "./tabs/cutting"
import DyeingTab from "./tabs/dyeing"
import KnittingTab from "./tabs/knitting"
import YarnTab from "./tabs/yarn"
import NewTicketTab from "./tabs/new-ticket"

interface TraceabilityDashboardProps {
  hash: string
  data: any
  onReset: () => void
}

export default function TraceabilityDashboard({ hash, data, onReset }: TraceabilityDashboardProps) {
  const [activeTab, setActiveTab] = useState("garment-info")
  const [copied, setCopied] = useState(false)
  const { theme, toggleTheme, language, setLanguage } = useTheme()
  const t = translations[language]

  const isDark = theme === "dark"
  const bgClass = isDark
    ? "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
    : "bg-gradient-to-br from-slate-50 via-white to-slate-100"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const cardBgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const headerBgClass = isDark ? "bg-slate-700 border-slate-600" : "bg-slate-100 border-slate-200"

  const endpoint = `https://api.gateway.ethswarm.org/bzz/${hash}`

  const copyHash = () => {
    navigator.clipboard.writeText(hash)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const tabs = [
    { id: "new-ticket", label: t.newTicket, icon: "🔍" },
    { id: "garment-info", label: t.garmentInfo, icon: "👕" },
    { id: "warehouse", label: t.warehouse, icon: "🏭" },
    { id: "finishing", label: t.garmentFinishing, icon: "✨" },
    { id: "sewing", label: t.sewing, icon: "🪡" },
    { id: "cutting", label: t.cutting, icon: "✂️" },
    { id: "dyeing", label: t.fabricDyeing, icon: "🎨" },
    { id: "knitting", label: t.knitting, icon: "🧶" },
    { id: "yarn", label: t.yarnSupplying, icon: "🧵" },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "new-ticket":
        return <NewTicketTab language={language} onSearch={onReset} />
      case "garment-info":
        return <GarmentInfoTab data={data} language={language} />
      case "warehouse":
        return <WarehouseTab data={data} language={language} />
      case "finishing":
        return <FinishingTab data={data} language={language} />
      case "sewing":
        return <SewingTab data={data} language={language} />
      case "cutting":
        return <CuttingTab data={data} language={language} />
      case "dyeing":
        return <DyeingTab data={data} language={language} />
      case "knitting":
        return <KnittingTab data={data} language={language} />
      case "yarn":
        return <YarnTab data={data} language={language} />
      default:
        return null
    }
  }

  return (
    <div className={`min-h-screen ${bgClass} py-8 px-4`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <Button
            onClick={onReset}
            variant="outline"
            className={`flex items-center gap-2 ${
              isDark
                ? "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"
                : "bg-slate-200 border-slate-300 text-slate-700 hover:bg-slate-300"
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
            {t.back}
          </Button>
          <h1 className={`text-3xl font-bold ${textClass}`}>{t.title}</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setLanguage(language === "en" ? "es" : "en")}
              className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                isDark
                  ? "bg-slate-700 hover:bg-slate-600 text-slate-300"
                  : "bg-slate-200 hover:bg-slate-300 text-slate-700"
              }`}
              title={language === "en" ? "Cambiar a Español" : "Switch to English"}
            >
              <span className="text-lg">{language === "en" ? "🇬🇧" : "🇪🇸"}</span>
              <span className="text-sm font-medium">{language === "en" ? "Language" : "Idioma"}</span>
            </button>
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? "bg-slate-700 hover:bg-slate-600 text-yellow-400"
                  : "bg-slate-200 hover:bg-slate-300 text-slate-700"
              }`}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Endpoint Info */}
        <div className={`${cardBgClass} border rounded-lg p-4 mb-8`}>
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex-1 min-w-0">
              <p className={`${subtextClass} text-sm mb-2`}>{t.endpointData}</p>
              <p className="text-emerald-400 text-sm font-mono break-all">{endpoint}</p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={copyHash}
                size="sm"
                className={`${
                  isDark
                    ? "bg-slate-700 hover:bg-slate-600 text-slate-300"
                    : "bg-slate-300 hover:bg-slate-400 text-slate-700"
                }`}
              >
                <Copy className="w-4 h-4" />
                {copied ? t.copied : t.copyHash}
              </Button>
              <a
                href={endpoint}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-sm transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                {t.viewJSON}
              </a>
            </div>
          </div>
        </div>

        {/* Tab Grid - 5 columns x 2 rows */}
        <div className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-center justify-center p-4 rounded-lg transition-all ${
                  activeTab === tab.id
                    ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/50"
                    : isDark
                      ? "bg-slate-700 text-slate-300 hover:bg-slate-600"
                      : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
              >
                <span className="text-2xl mb-2">{tab.icon}</span>
                <span className="text-xs text-center font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className={`${cardBgClass} border rounded-lg p-6`}>{renderTabContent()}</div>
      </div>
    </div>
  )
}
