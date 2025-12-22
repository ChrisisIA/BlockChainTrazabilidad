"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle, Loader2, Search, ChevronLeft, ChevronRight } from "lucide-react"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"

interface FilterData {
  TTICKBARR: string
  TNUMEVERS: number
  TNUMECAJA: string
  TESTICLIE: string
  TETIQCLIE: string
  TCODITALL: string
  TTICKHASH: string
  TFECHGUAR: string
}

interface FilterResponse {
  success: boolean
  count: number
  data: FilterData[]
  message?: string
}

export default function FilterTable() {
  const [numecaja, setNumecaja] = useState("")
  const [esticlie, setEsticlie] = useState("")
  const [etiqclie, setEtiqclie] = useState("")
  const [coditall, setCoditall] = useState("")

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<FilterData[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

  const { theme, language } = useTheme()
  const t = translations[language]

  const itemsPerPage = 10

  const isDark = theme === "dark"
  const cardBgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const inputBgClass = isDark
    ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400"
    : "bg-slate-100 border-slate-300 text-slate-900 placeholder-slate-500"
  const tableBgClass = isDark ? "bg-slate-700" : "bg-slate-50"
  const tableHeaderClass = isDark ? "bg-slate-600 text-slate-200" : "bg-slate-200 text-slate-700"
  const tableRowClass = isDark ? "hover:bg-slate-600 border-slate-600" : "hover:bg-slate-100 border-slate-200"

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validar que al menos un campo tenga valor
    if (!numecaja && !esticlie && !etiqclie && !coditall) {
      setError(language === "en" ? "Please enter at least one filter" : "Por favor ingresa al menos un filtro")
      return
    }

    setLoading(true)
    setError(null)
    setData([])
    setCurrentPage(1)

    try {
      const filters: Record<string, string> = {}
      if (numecaja) filters.numecaja = numecaja
      if (esticlie) filters.esticlie = esticlie
      if (etiqclie) filters.etiqclie = etiqclie
      if (coditall) filters.coditall = coditall

      const response = await fetch("http://128.0.17.5:5000/filter_data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(filters),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Error fetching data")
      }

      const result: FilterResponse = await response.json()

      if (result.success) {
        setData(result.data)
        setTotalCount(result.count)
        if (result.count === 0) {
          setError(language === "en" ? "No results found" : "No se encontraron resultados")
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error fetching data"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setNumecaja("")
    setEsticlie("")
    setEtiqclie("")
    setCoditall("")
    setData([])
    setError(null)
    setCurrentPage(1)
    setTotalCount(0)
  }

  // Paginación
  const totalPages = Math.ceil(data.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentData = data.slice(startIndex, endIndex)

  const goToPage = (page: number) => {
    setCurrentPage(page)
  }

  return (
    <div className={`${cardBgClass} rounded-xl p-6 md:p-8 border shadow-xl mt-8`}>
      <h2 className={`text-xl md:text-2xl font-bold ${textClass} mb-6 text-center`}>
        {language === "en" ? "Advanced Filter" : "Filtro Avanzado"}
      </h2>

      <form onSubmit={handleSearch} className="space-y-4">
        {/* Grid de 2x2 para los inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className={`block text-sm font-medium ${subtextClass} mb-1`}>
              {language === "en" ? "Box Number" : "Número de Caja"}
            </label>
            <Input
              type="text"
              placeholder={language === "en" ? "Enter box number..." : "Ingresa número de caja..."}
              value={numecaja}
              onChange={(e) => setNumecaja(e.target.value)}
              disabled={loading}
              className={`w-full px-4 py-3 text-base ${inputBgClass} rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50`}
            />
          </div>

          <div>
            <label className={`block text-sm font-medium ${subtextClass} mb-1`}>
              {language === "en" ? "Client Style" : "Estilo Cliente"}
            </label>
            <Input
              type="text"
              placeholder={language === "en" ? "Enter client style..." : "Ingresa estilo cliente..."}
              value={esticlie}
              onChange={(e) => setEsticlie(e.target.value)}
              disabled={loading}
              className={`w-full px-4 py-3 text-base ${inputBgClass} rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50`}
            />
          </div>

          <div>
            <label className={`block text-sm font-medium ${subtextClass} mb-1`}>
              {language === "en" ? "Client Label" : "Etiqueta Cliente"}
            </label>
            <Input
              type="text"
              placeholder={language === "en" ? "Enter client label..." : "Ingresa etiqueta cliente..."}
              value={etiqclie}
              onChange={(e) => setEtiqclie(e.target.value)}
              disabled={loading}
              className={`w-full px-4 py-3 text-base ${inputBgClass} rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50`}
            />
          </div>

          <div>
            <label className={`block text-sm font-medium ${subtextClass} mb-1`}>
              {language === "en" ? "Size" : "Talla"}
            </label>
            <Input
              type="text"
              placeholder={language === "en" ? "Enter size..." : "Ingresa talla..."}
              value={coditall}
              onChange={(e) => setCoditall(e.target.value)}
              disabled={loading}
              className={`w-full px-4 py-3 text-base ${inputBgClass} rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 disabled:opacity-50`}
            />
          </div>
        </div>

        {/* Botones */}
        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={loading || (!numecaja && !esticlie && !etiqclie && !coditall)}
            className="flex-1 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {language === "en" ? "Searching..." : "Buscando..."}
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                {language === "en" ? "Search" : "Buscar"}
              </>
            )}
          </Button>

          <Button
            type="button"
            onClick={handleClear}
            disabled={loading}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              isDark
                ? "bg-slate-700 hover:bg-slate-600 text-slate-300"
                : "bg-slate-200 hover:bg-slate-300 text-slate-700"
            } disabled:opacity-50`}
          >
            {language === "en" ? "Clear" : "Limpiar"}
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-400 text-sm">{error}</span>
          </div>
        )}
      </form>

      {/* Tabla de Resultados */}
      {data.length > 0 && (
        <div className="mt-6 space-y-4">
          <div className={`text-sm ${subtextClass} font-medium`}>
            {language === "en" ? `Found ${totalCount} results` : `Se encontraron ${totalCount} resultados`}
          </div>

          {/* Tabla - Responsive */}
          <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
            <table className="w-full text-sm">
              <thead className={tableHeaderClass}>
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">Tickbarr</th>
                  <th className="px-4 py-3 text-left font-semibold">{language === "en" ? "Box" : "Caja"}</th>
                  <th className="px-4 py-3 text-left font-semibold">{language === "en" ? "Style" : "Estilo"}</th>
                  <th className="px-4 py-3 text-left font-semibold">{language === "en" ? "Label" : "Etiqueta"}</th>
                  <th className="px-4 py-3 text-left font-semibold">{language === "en" ? "Size" : "Talla"}</th>
                  <th className="px-4 py-3 text-left font-semibold">Hash</th>
                  <th className="px-4 py-3 text-left font-semibold">{language === "en" ? "Date" : "Fecha"}</th>
                </tr>
              </thead>
              <tbody className={tableBgClass}>
                {currentData.map((row, index) => (
                  <tr key={`${row.TTICKBARR}-${index}`} className={`border-t ${tableRowClass}`}>
                    <td className={`px-4 py-3 font-mono ${textClass}`}>{row.TTICKBARR}</td>
                    <td className={`px-4 py-3 ${textClass}`}>{row.TNUMECAJA}</td>
                    <td className={`px-4 py-3 ${textClass}`}>{row.TESTICLIE}</td>
                    <td className={`px-4 py-3 ${textClass}`}>{row.TETIQCLIE}</td>
                    <td className={`px-4 py-3 ${textClass}`}>{row.TCODITALL}</td>
                    <td className={`px-4 py-3 font-mono text-xs ${subtextClass}`} title={row.TTICKHASH}>
                      {row.TTICKHASH.substring(0, 12)}...
                    </td>
                    <td className={`px-4 py-3 ${subtextClass} text-xs`}>{row.TFECHGUAR}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className={`text-sm ${subtextClass}`}>
                {language === "en"
                  ? `Page ${currentPage} of ${totalPages}`
                  : `Página ${currentPage} de ${totalPages}`}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={`p-2 rounded-lg transition-colors ${
                    isDark
                      ? "bg-slate-700 hover:bg-slate-600 text-slate-300 disabled:opacity-30"
                      : "bg-slate-200 hover:bg-slate-300 text-slate-700 disabled:opacity-30"
                  } disabled:cursor-not-allowed`}
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>

                {/* Números de página */}
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter(
                    (page) =>
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1),
                  )
                  .map((page, index, array) => (
                    <React.Fragment key={page}>
                      {index > 0 && array[index - 1] !== page - 1 && (
                        <span className={`px-2 ${subtextClass}`}>...</span>
                      )}
                      <button
                        onClick={() => goToPage(page)}
                        className={`px-3 py-2 rounded-lg transition-colors font-medium ${
                          currentPage === page
                            ? "bg-emerald-600 text-white"
                            : isDark
                              ? "bg-slate-700 hover:bg-slate-600 text-slate-300"
                              : "bg-slate-200 hover:bg-slate-300 text-slate-700"
                        }`}
                      >
                        {page}
                      </button>
                    </React.Fragment>
                  ))}

                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className={`p-2 rounded-lg transition-colors ${
                    isDark
                      ? "bg-slate-700 hover:bg-slate-600 text-slate-300 disabled:opacity-30"
                      : "bg-slate-200 hover:bg-slate-300 text-slate-700 disabled:opacity-30"
                  } disabled:cursor-not-allowed`}
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
