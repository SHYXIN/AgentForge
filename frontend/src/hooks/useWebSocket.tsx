import React, { createContext, useContext, useEffect, useRef, useState } from 'react'

interface WebSocketContextType {
  isConnected: boolean
  lastMessage: string | null
  sendMessage: (message: string) => void
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

interface WebSocketProviderProps {
  url: string
  children: React.ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ url, children }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    try {
      wsRef.current = new WebSocket(url)

      wsRef.current.onopen = () => {
        console.log('WebSocket 连接已建立')
        setIsConnected(true)
        reconnectAttempts.current = 0
      }

      wsRef.current.onmessage = (event) => {
        console.log('收到消息:', event.data)
        setLastMessage(event.data)
      }

      wsRef.current.onclose = () => {
        console.log('WebSocket 连接已关闭')
        setIsConnected(false)
        
        // 自动重连逻辑
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000 // 指数退避
          reconnectAttempts.current++
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`尝试重连... (${reconnectAttempts.current}/${maxReconnectAttempts})`)
            connect()
          }, delay)
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket 错误:', error)
        setIsConnected(false)
      }

    } catch (error) {
      console.error('WebSocket 连接失败:', error)
      setIsConnected(false)
    }
  }

  const sendMessage = (message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
      console.log('发送消息:', message)
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }

  useEffect(() => {
    connect()

    return () => {
      // 清理函数
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [url])

  const value: WebSocketContextType = {
    isConnected,
    lastMessage,
    sendMessage
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket 必须在 WebSocketProvider 内部使用')
  }
  return context
}
