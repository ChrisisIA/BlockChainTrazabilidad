"use client"

import type React from "react"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { useTheme } from "@/lib/theme-context"
import { translations } from "@/lib/i18n"
import { Mail, Lock, Moon, Sun } from "lucide-react"

export default function LoginForm() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [localError, setLocalError] = useState<string | null>(null)
  const { login, isLoading, error } = useAuth()
  const { theme, toggleTheme, language, setLanguage } = useTheme()
  const t = translations[language]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    if (!username || !password) {
      setLocalError("Please fill in all fields")
      return
    }

    try {
      await login(username, password)
    } catch {
      setLocalError(error || "Login failed")
    }
  }

  const bgClass =
    theme === "dark"
      ? "min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
      : "min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100"

  const cardClass =
    theme === "dark" ? "bg-slate-800 border-slate-700 shadow-2xl" : "bg-white border-slate-200 shadow-xl"

  const inputClass =
    theme === "dark"
      ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400 focus:border-emerald-500"
      : "bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-500 focus:border-emerald-500"

  const buttonClass =
    isLoading || !username || !password
      ? "bg-emerald-600 text-white opacity-50 cursor-not-allowed"
      : "bg-emerald-600 hover:bg-emerald-700 text-white"

  return (
    <main className={bgClass}>
      <div className="flex min-h-screen items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center justify-between">
            <button
              onClick={toggleTheme}
              className={`rounded-lg p-2 transition-colors ${
                theme === "dark" ? "bg-slate-700 text-yellow-400" : "bg-slate-200 text-slate-700"
              } hover:opacity-80`}
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => setLanguage("en")}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  language === "en"
                    ? "bg-emerald-600 text-white"
                    : theme === "dark"
                      ? "bg-slate-700 text-slate-300 hover:bg-slate-600"
                      : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage("es")}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  language === "es"
                    ? "bg-emerald-600 text-white"
                    : theme === "dark"
                      ? "bg-slate-700 text-slate-300 hover:bg-slate-600"
                      : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                }`}
              >
                ES
              </button>
            </div>
          </div>

          <div className={`border px-6 py-8 rounded-lg ${cardClass}`}>
            <div className="mb-8 text-center">
              <h1 className={`text-3xl font-bold mb-2 ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                {t.loginTitle}
              </h1>
              <p className={`text-sm ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}>{t.loginSubtitle}</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}
                >
                  {t.username}
                </label>
                <div className="relative">
                  <Mail
                    className={`absolute left-3 top-3 size-5 ${theme === "dark" ? "text-slate-500" : "text-slate-400"}`}
                  />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder={t.enterUsername}
                    className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${inputClass}`}
                  />
                </div>
              </div>

              <div>
                <label
                  className={`block text-sm font-medium mb-2 ${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}
                >
                  {t.password}
                </label>
                <div className="relative">
                  <Lock
                    className={`absolute left-3 top-3 size-5 ${theme === "dark" ? "text-slate-500" : "text-slate-400"}`}
                  />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t.enterPassword}
                    className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${inputClass}`}
                  />
                </div>
              </div>

              {(localError || error) && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{localError || error}</div>
              )}

              <button
                type="submit"
                disabled={isLoading || !username || !password}
                className={`w-full py-2 rounded-lg font-medium transition-colors ${buttonClass}`}
              >
                {isLoading ? t.loadingLogin : t.signIn}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  )
}
