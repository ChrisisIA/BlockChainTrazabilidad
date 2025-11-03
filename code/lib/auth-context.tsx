"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

interface AuthContextType {
  token: string | null
  username: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [username, setUsername] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token")
    const savedUsername = localStorage.getItem("auth_username")
    if (savedToken) {
      setToken(savedToken)
      setUsername(savedUsername)
    }
    setMounted(true)
  }, [])

  const login = async (user: string, pass: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch("http://128.0.17.5:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: user,
          password: pass,
        }),
      })

      if (!response.ok) {
        throw new Error("Invalid credentials")
      }

      const data = await response.json()
      setToken(data.access_token)
      setUsername(user)
      localStorage.setItem("auth_token", data.access_token)
      localStorage.setItem("auth_username", user)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setToken(null)
    setUsername(null)
    localStorage.removeItem("auth_token")
    localStorage.removeItem("auth_username")
  }

  return (
    <AuthContext.Provider value={{ token, username, login, logout, isLoading, error }}>{children}</AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
