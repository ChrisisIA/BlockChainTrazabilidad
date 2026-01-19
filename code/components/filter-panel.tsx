"use client"

import { useState, useEffect } from "react"
import { useTheme } from "@/lib/theme-context"
import { translations, type Language } from "@/lib/i18n"
import { ChevronDown, ChevronUp, Filter, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FilterPanelProps {
  language: Language
  onApplyFilters?: (filters: FilterState) => void
  externalFilters?: Partial<FilterState>
}

export interface FilterState {
  client: string
  clientStyle: string
  boxNumber: string
  label: string
  size: string
  gender: string
  age: string
  garmentType: string
}

const initialFilters: FilterState = {
  client: "",
  clientStyle: "",
  boxNumber: "",
  label: "",
  size: "",
  gender: "",
  age: "",
  garmentType: "",
}

export default function FilterPanel({ language, onApplyFilters, externalFilters }: FilterPanelProps) {
  const { theme } = useTheme()
  const t = translations[language]
  const isDark = theme === "dark"

  const [filters, setFilters] = useState<FilterState>(initialFilters)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [recentlyUpdated, setRecentlyUpdated] = useState<Set<string>>(new Set())

  // Sincronizar filtros externos (del chat) con el estado local
  useEffect(() => {
    if (externalFilters) {
      const updatedFields: string[] = []

      setFilters((prev) => {
        const newFilters = { ...prev }
        Object.entries(externalFilters).forEach(([key, value]) => {
          const filterKey = key as keyof FilterState
          // Solo actualizar campos vacíos (no sobrescribir filtros manuales)
          if (value && String(value).trim() && !prev[filterKey]) {
            newFilters[filterKey] = String(value)
            updatedFields.push(key)
          }
        })
        return newFilters
      })

      // Resaltar campos actualizados temporalmente
      if (updatedFields.length > 0) {
        setRecentlyUpdated(new Set(updatedFields))
        // Quitar resaltado después de 2 segundos
        setTimeout(() => {
          setRecentlyUpdated(new Set())
        }, 2000)
      }
    }
  }, [externalFilters])

  const bgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const inputBgClass = isDark
    ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400"
    : "bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-500"

  const filterLabels = {
    client: language === "en" ? "Client" : "Cliente",
    clientStyle: language === "en" ? "Client Style" : "Estilo Cliente",
    boxNumber: language === "en" ? "Box Number" : "Número de Caja",
    label: language === "en" ? "Label" : "Etiqueta",
    size: language === "en" ? "Size" : "Talla",
    gender: language === "en" ? "Gender" : "Género",
    age: language === "en" ? "Age" : "Edad",
    garmentType: language === "en" ? "Garment Type" : "Tipo de Prenda",
  }

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleApplyFilters = () => {
    onApplyFilters?.(filters)
  }

  const handleClearFilters = () => {
    setFilters(initialFilters)
    onApplyFilters?.(initialFilters)
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== "")

  return (
    <div className={`${bgClass} border rounded-lg overflow-hidden`}>
      {/* Header */}
      <div
        className={`flex items-center justify-between p-4 cursor-pointer ${
          isDark ? "bg-slate-700/50" : "bg-slate-100"
        }`}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2">
          <Filter className={`w-5 h-5 ${textClass}`} />
          <h3 className={`font-semibold ${textClass}`}>
            {language === "en" ? "Filters" : "Filtros"}
          </h3>
          {hasActiveFilters && (
            <span className="bg-emerald-500 text-white text-xs px-2 py-0.5 rounded-full">
              {Object.values(filters).filter(v => v !== "").length}
            </span>
          )}
        </div>
        {isCollapsed ? (
          <ChevronDown className={`w-5 h-5 ${subtextClass}`} />
        ) : (
          <ChevronUp className={`w-5 h-5 ${subtextClass}`} />
        )}
      </div>

      {/* Filter Fields */}
      {!isCollapsed && (
        <div className="p-4 space-y-4">
          {Object.entries(filterLabels).map(([key, label]) => {
            const isRecentlyUpdated = recentlyUpdated.has(key)
            return (
              <div key={key}>
                <label className={`block text-sm font-medium ${subtextClass} mb-1 flex items-center gap-2`}>
                  {label}
                  {isRecentlyUpdated && (
                    <span className="text-xs text-emerald-500 animate-pulse">
                      {language === "en" ? "Auto-filled" : "Auto-completado"}
                    </span>
                  )}
                </label>
                <input
                  type="text"
                  value={filters[key as keyof FilterState]}
                  onChange={(e) => handleFilterChange(key as keyof FilterState, e.target.value)}
                  placeholder={`${language === "en" ? "Enter" : "Ingrese"} ${label.toLowerCase()}...`}
                  className={`w-full px-3 py-2 rounded-lg border text-sm ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all duration-300 ${
                    isRecentlyUpdated ? "ring-2 ring-emerald-500 border-emerald-500" : ""
                  }`}
                />
              </div>
            )
          })}

          {/* Action Buttons */}
          <div className="flex flex-col gap-2 pt-2">
            <Button
              onClick={handleApplyFilters}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              {language === "en" ? "Apply Filters" : "Aplicar Filtros"}
            </Button>
            {hasActiveFilters && (
              <Button
                onClick={handleClearFilters}
                variant="outline"
                className={`w-full flex items-center justify-center gap-2 ${
                  isDark
                    ? "border-slate-600 text-slate-300 hover:bg-slate-700"
                    : "border-slate-300 text-slate-700 hover:bg-slate-100"
                }`}
              >
                <X className="w-4 h-4" />
                {language === "en" ? "Clear Filters" : "Limpiar Filtros"}
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
