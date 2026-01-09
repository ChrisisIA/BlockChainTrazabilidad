"use client"

import { useState } from "react"
import HashInput from "@/components/hash-input"
import TraceabilityDashboard from "@/components/traceability-dashboard"
import { useTheme } from "@/lib/theme-context"
import LoginForm from "@/components/login-form"
import { useAuth } from "@/lib/auth-context"

export default function Home() {
  const [hash, setHash] = useState<string | null>(null)
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { theme } = useTheme()
  const { token } = useAuth()

  if (!token) {
    return <LoginForm />
  }

  const handleHashSubmit = async (hash: string) => {
    setLoading(true)
    setError(null)
    setData(null)

    try {
      // Obtener datos de Swarm a través del backend proxy
      const response = await fetch("http://128.0.17.5:5000/get_swarm_data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ hash }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Error fetching data: ${response.statusText}`)
      }

      const jsonData = await response.json()
      setHash(hash)
      setData(jsonData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error fetching data")
      setHash(null)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  const bgClass =
    theme === "dark"
      ? "min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
      : "min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100"

  return (
    <main className={bgClass}>
      {!hash ? (
        <HashInput onSubmit={handleHashSubmit} loading={loading} error={error} />
      ) : (
        <TraceabilityDashboard hash={hash} data={data} onReset={() => setHash(null)} />
      )}
    </main>
  )
}
