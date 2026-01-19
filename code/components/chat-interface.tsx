"use client"

import { useState, useRef, useEffect } from "react"
import { useTheme } from "@/lib/theme-context"
import { type Language } from "@/lib/i18n"
import { Send, Bot, User, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { type FilterState } from "./filter-panel"

interface ChatInterfaceProps {
  language: Language
  filters?: FilterState
  onFiltersExtracted?: (filters: FilterState, corrections?: Record<string, string>) => void
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

const BACKEND_URL = "http://128.0.17.5:5000"

export default function ChatInterface({ language, filters, onFiltersExtracted }: ChatInterfaceProps) {
  const { theme } = useTheme()
  const isDark = theme === "dark"

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: language === "en"
        ? "Hello! I'm your traceability assistant. Ask me anything about the garment data in the blockchain."
        : "¡Hola! Soy tu asistente de trazabilidad. Pregúntame lo que quieras sobre los datos de las prendas en la blockchain.",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const bgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const inputBgClass = isDark
    ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400"
    : "bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-500"
  const messageBgUser = isDark ? "bg-emerald-600" : "bg-emerald-500"
  const messageBgAssistant = isDark ? "bg-slate-700" : "bg-slate-100"

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userMessage.content,
          model: "deepseek",
          filters: filters || {},
        }),
      })

      const data = await response.json()

      let assistantContent: string
      if (data.success && data.response) {
        assistantContent = data.response

        // Notificar al padre sobre filtros extraídos para sincronización bidireccional
        if (data.extracted_filters && onFiltersExtracted) {
          const hasExtractedValues = Object.values(data.extracted_filters).some(
            (v) => v && String(v).trim() !== ""
          )
          if (hasExtractedValues) {
            onFiltersExtracted(data.extracted_filters, data.corrections || undefined)
          }
        }
      } else if (data.error) {
        assistantContent = language === "en"
          ? `Error: ${data.error}`
          : `Error: ${data.error}`
      } else {
        assistantContent = language === "en"
          ? "Sorry, I couldn't process your request. Please try again."
          : "Lo siento, no pude procesar tu solicitud. Por favor intenta de nuevo."
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: assistantContent,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error("Error calling chat API:", error)
      const errorMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: language === "en"
          ? "Connection error. Please check that the server is running and try again."
          : "Error de conexión. Por favor verifica que el servidor esté funcionando e intenta de nuevo.",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(language === "en" ? "en-US" : "es-ES", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className={`${bgClass} border rounded-lg flex flex-col h-full min-h-[500px]`}>
      {/* Header */}
      <div
        className={`flex items-center gap-3 p-4 border-b ${
          isDark ? "border-slate-700 bg-slate-700/50" : "border-slate-200 bg-slate-50"
        }`}
      >
        <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className={`font-semibold ${textClass}`}>
            {language === "en" ? "Traceability Assistant" : "Asistente de Trazabilidad"}
          </h3>
          <p className={`text-sm ${subtextClass}`}>
            {language === "en" ? "Ask about garment data" : "Pregunta sobre datos de la prenda"}
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                message.role === "user"
                  ? "bg-emerald-500"
                  : isDark
                    ? "bg-slate-600"
                    : "bg-slate-300"
              }`}
            >
              {message.role === "user" ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className={`w-4 h-4 ${isDark ? "text-white" : "text-slate-700"}`} />
              )}
            </div>

            {/* Message Bubble */}
            <div
              className={`max-w-[75%] rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? `${messageBgUser} text-white`
                  : `${messageBgAssistant} ${textClass}`
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p
                className={`text-xs mt-1 ${
                  message.role === "user" ? "text-emerald-100" : subtextClass
                }`}
              >
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div
              className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                isDark ? "bg-slate-600" : "bg-slate-300"
              }`}
            >
              <Bot className={`w-4 h-4 ${isDark ? "text-white" : "text-slate-700"}`} />
            </div>
            <div className={`rounded-lg px-4 py-3 ${messageBgAssistant}`}>
              <div className="flex items-center gap-2">
                <Loader2 className={`w-5 h-5 animate-spin ${subtextClass}`} />
                <span className={`text-sm ${subtextClass}`}>
                  {language === "en" ? "Thinking..." : "Pensando..."}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        className={`p-4 border-t ${
          isDark ? "border-slate-700" : "border-slate-200"
        }`}
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              language === "en"
                ? "Type your question..."
                : "Escribe tu pregunta..."
            }
            disabled={isLoading}
            className={`flex-1 px-4 py-2 rounded-lg border ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:opacity-50`}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
        <p className={`text-xs ${subtextClass} mt-2 text-center`}>
          {language === "en"
            ? "Press Enter to send your message"
            : "Presiona Enter para enviar tu mensaje"}
        </p>
      </div>
    </div>
  )
}
