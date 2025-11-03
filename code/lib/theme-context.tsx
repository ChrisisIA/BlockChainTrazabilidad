"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

type Theme = "light" | "dark"
type Language = "en" | "es"

interface ThemeContextType {
  theme: Theme
  language: Language
  toggleTheme: () => void
  setLanguage: (lang: Language) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("dark")
  const [language, setLanguageSt] = useState<Language>("en")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const savedTheme = (localStorage.getItem("theme") as Theme) || "dark"
    const savedLanguage = (localStorage.getItem("language") as Language) || "en"

    setTheme(savedTheme)
    setLanguageSt(savedLanguage)
    setMounted(true)

    const html = document.documentElement
    if (savedTheme === "dark") {
      html.classList.add("dark")
    } else {
      html.classList.remove("dark")
    }
  }, [])

  useEffect(() => {
    if (!mounted) return
    localStorage.setItem("theme", theme)
    const html = document.documentElement
    if (theme === "dark") {
      html.classList.add("dark")
    } else {
      html.classList.remove("dark")
    }
  }, [theme, mounted])

  useEffect(() => {
    if (!mounted) return
    localStorage.setItem("language", language)
  }, [language, mounted])

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"))
  }

  const setLanguage = (lang: Language) => {
    setLanguageSt(lang)
  }

  return <ThemeContext.Provider value={{ theme, language, toggleTheme, setLanguage }}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider")
  }
  return context
}
