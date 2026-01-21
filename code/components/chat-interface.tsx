"use client"

import { useState, useRef, useEffect } from "react"
import { useTheme } from "@/lib/theme-context"
import { useAuth } from "@/lib/auth-context"
import { type Language } from "@/lib/i18n"
import { Send, Bot, User, Loader2, Plus, MessageSquare, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
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

interface Conversation {
  group_id: number
  first_question: string
  start_date: string
}

const BACKEND_URL = "http://128.0.17.5:5000"

export default function ChatInterface({ language, filters, onFiltersExtracted }: ChatInterfaceProps) {
  const { theme } = useTheme()
  const { userCode, username } = useAuth()
  const isDark = theme === "dark"

  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [conversationGroup, setConversationGroup] = useState<number | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [showSidebar, setShowSidebar] = useState(false)
  const [loadingConversations, setLoadingConversations] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const bgClass = isDark ? "bg-slate-800 border-slate-700" : "bg-white border-slate-200"
  const textClass = isDark ? "text-white" : "text-slate-900"
  const subtextClass = isDark ? "text-slate-400" : "text-slate-600"
  const inputBgClass = isDark
    ? "bg-slate-700 border-slate-600 text-white placeholder-slate-400"
    : "bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-500"
  const messageBgUser = isDark ? "bg-emerald-600" : "bg-emerald-500"
  const messageBgAssistant = isDark ? "bg-slate-700" : "bg-slate-100"
  const sidebarBgClass = isDark ? "bg-slate-900 border-slate-700" : "bg-slate-50 border-slate-200"

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Cargar conversaciones del usuario al montar el componente
  useEffect(() => {
    if (userCode) {
      loadConversations()
      loadCurrentGroup()
    }
  }, [userCode])

  const loadConversations = async () => {
    if (!userCode) return
    setLoadingConversations(true)
    try {
      const response = await fetch(`${BACKEND_URL}/chat/conversations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_code: userCode }),
      })
      const data = await response.json()
      if (data.success) {
        setConversations(data.conversations)
      }
    } catch (error) {
      console.error("Error loading conversations:", error)
    } finally {
      setLoadingConversations(false)
    }
  }

  const loadCurrentGroup = async () => {
    if (!userCode) return
    try {
      const response = await fetch(`${BACKEND_URL}/chat/current_group`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_code: userCode }),
      })
      const data = await response.json()
      if (data.success && data.conversation_group) {
        setConversationGroup(data.conversation_group)
        loadChatHistory(data.conversation_group)
      } else {
        // Si no hay grupo actual, iniciar con mensaje de bienvenida
        setWelcomeMessage()
      }
    } catch (error) {
      console.error("Error loading current group:", error)
      setWelcomeMessage()
    }
  }

  const setWelcomeMessage = () => {
    setMessages([{
      id: "welcome",
      role: "assistant",
      content: language === "en"
        ? "Hello! I'm your traceability assistant. Ask me anything about the garment data in the blockchain."
        : "¡Hola! Soy tu asistente de trazabilidad. Pregúntame lo que quieras sobre los datos de las prendas en la blockchain.",
      timestamp: new Date(),
    }])
  }

  const loadChatHistory = async (groupId: number) => {
    if (!userCode) return
    try {
      const response = await fetch(`${BACKEND_URL}/chat/history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          conversation_group: groupId,
        }),
      })
      const data = await response.json()
      if (data.success && data.history.length > 0) {
        const historyMessages: Message[] = []
        data.history.forEach((entry: { question: string; answer: string; timestamp: string }, index: number) => {
          historyMessages.push({
            id: `user-hist-${index}`,
            role: "user",
            content: entry.question,
            timestamp: new Date(entry.timestamp),
          })
          historyMessages.push({
            id: `assistant-hist-${index}`,
            role: "assistant",
            content: entry.answer,
            timestamp: new Date(entry.timestamp),
          })
        })
        setMessages(historyMessages)
      } else {
        setWelcomeMessage()
      }
    } catch (error) {
      console.error("Error loading chat history:", error)
      setWelcomeMessage()
    }
  }

  const startNewConversation = async () => {
    if (!userCode) return
    try {
      const response = await fetch(`${BACKEND_URL}/chat/new_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_code: userCode }),
      })
      const data = await response.json()
      if (data.success) {
        setConversationGroup(data.conversation_group)
        setWelcomeMessage()
        loadConversations() // Recargar lista de conversaciones
      }
    } catch (error) {
      console.error("Error creating new conversation:", error)
    }
  }

  const selectConversation = async (groupId: number) => {
    setConversationGroup(groupId)
    await loadChatHistory(groupId)
    setShowSidebar(false)
  }

  const deleteConversation = async (groupId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!userCode) return

    const confirmMessage = language === "en"
      ? "Are you sure you want to delete this conversation?"
      : "¿Estás seguro de que deseas eliminar esta conversación?"

    if (!confirm(confirmMessage)) return

    try {
      const response = await fetch(`${BACKEND_URL}/chat/delete_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          conversation_group: groupId,
        }),
      })
      const data = await response.json()
      if (data.success) {
        loadConversations()
        if (conversationGroup === groupId) {
          setConversationGroup(null)
          setWelcomeMessage()
        }
      }
    } catch (error) {
      console.error("Error deleting conversation:", error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    // Si no hay grupo de conversacion, crear uno nuevo
    let currentGroup = conversationGroup
    if (!currentGroup && userCode) {
      try {
        const response = await fetch(`${BACKEND_URL}/chat/new_conversation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_code: userCode }),
        })
        const data = await response.json()
        if (data.success) {
          currentGroup = data.conversation_group
          setConversationGroup(currentGroup)
        }
      } catch (error) {
        console.error("Error creating conversation group:", error)
      }
    }

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
          user_code: userCode,
          user_name: username,
          conversation_group: currentGroup,
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

      // Recargar lista de conversaciones si es un mensaje nuevo
      if (messages.length <= 1) {
        loadConversations()
      }

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
    <div className={`${bgClass} border rounded-lg flex h-full min-h-[500px]`}>
      {/* Sidebar de conversaciones */}
      <div
        className={`${sidebarBgClass} border-r transition-all duration-300 flex flex-col ${
          showSidebar ? "w-64" : "w-0 overflow-hidden"
        }`}
      >
        {showSidebar && (
          <>
            {/* Header del sidebar */}
            <div className={`p-3 border-b ${isDark ? "border-slate-700" : "border-slate-200"}`}>
              <Button
                onClick={startNewConversation}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white"
                size="sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                {language === "en" ? "New Chat" : "Nuevo Chat"}
              </Button>
            </div>

            {/* Lista de conversaciones */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {loadingConversations ? (
                <div className="flex justify-center py-4">
                  <Loader2 className={`w-5 h-5 animate-spin ${subtextClass}`} />
                </div>
              ) : conversations.length === 0 ? (
                <p className={`text-sm ${subtextClass} text-center py-4`}>
                  {language === "en" ? "No previous chats" : "Sin chats anteriores"}
                </p>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.group_id}
                    onClick={() => selectConversation(conv.group_id)}
                    className={`p-2 rounded-lg cursor-pointer flex items-start gap-2 group ${
                      conversationGroup === conv.group_id
                        ? isDark
                          ? "bg-slate-700"
                          : "bg-slate-200"
                        : isDark
                          ? "hover:bg-slate-800"
                          : "hover:bg-slate-100"
                    }`}
                  >
                    <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${subtextClass}`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm ${textClass} truncate`}>
                        {conv.first_question}
                      </p>
                      <p className={`text-xs ${subtextClass}`}>
                        {conv.start_date}
                      </p>
                    </div>
                    <button
                      onClick={(e) => deleteConversation(conv.group_id, e)}
                      className={`opacity-0 group-hover:opacity-100 p-1 rounded ${
                        isDark ? "hover:bg-slate-600" : "hover:bg-slate-300"
                      }`}
                    >
                      <Trash2 className="w-3 h-3 text-red-500" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div
          className={`flex items-center gap-3 p-4 border-b ${
            isDark ? "border-slate-700 bg-slate-700/50" : "border-slate-200 bg-slate-50"
          }`}
        >
          {/* Toggle sidebar button */}
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className={`p-2 rounded-lg ${
              isDark ? "hover:bg-slate-600" : "hover:bg-slate-200"
            }`}
          >
            {showSidebar ? (
              <ChevronLeft className={`w-5 h-5 ${textClass}`} />
            ) : (
              <ChevronRight className={`w-5 h-5 ${textClass}`} />
            )}
          </button>

          <div className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className={`font-semibold ${textClass}`}>
              {language === "en" ? "Traceability Assistant" : "Asistente de Trazabilidad"}
            </h3>
            <p className={`text-sm ${subtextClass}`}>
              {language === "en" ? "Ask about garment data" : "Pregunta sobre datos de la prenda"}
            </p>
          </div>

          {/* Nuevo chat button en header */}
          <Button
            onClick={startNewConversation}
            variant="outline"
            size="sm"
            className={isDark ? "border-slate-600 hover:bg-slate-700" : ""}
          >
            <Plus className="w-4 h-4 mr-1" />
            {language === "en" ? "New" : "Nuevo"}
          </Button>
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
    </div>
  )
}
