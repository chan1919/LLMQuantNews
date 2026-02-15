import { useState, useEffect, createContext, useContext } from 'react'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Snackbar,
  Alert,
} from '@mui/material'
import {
  Menu as MenuIcon,
  DynamicFeed as FeedIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'

const drawerWidth = 240

const menuItems = [
  { text: '信息流', icon: <FeedIcon />, path: '/' },
  { text: '历史记录', icon: <HistoryIcon />, path: '/history' },
  { text: '配置管理', icon: <SettingsIcon />, path: '/config' },
  { text: '成本统计', icon: <MoneyIcon />, path: '/costs' },
]

// 创建 WebSocket 上下文
interface WebSocketContextType {
  ws: WebSocket | null
  isConnected: boolean
  latestData: any
  sendMessage: (message: any) => void
}

const WebSocketContext = createContext<WebSocketContextType>({
  ws: null,
  isConnected: false,
  latestData: null,
  sendMessage: () => {},
})

// 自定义 Hook，用于使用 WebSocket 上下文
export const useWebSocket = () => useContext(WebSocketContext)

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [latestData, setLatestData] = useState<any>(null)
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' | 'info' | 'warning' } | null>(null)
  const navigate = useNavigate()
  const location = useLocation()

  // 处理 WebSocket 连接
  useEffect(() => {
    let socket: WebSocket | null = null
    let heartbeatInterval: NodeJS.Timeout | null = null
    let reconnectTimeout: NodeJS.Timeout | null = null
    let reconnectAttempts = 0
    const maxReconnectAttempts = 10 // 增加最大重连次数
    const baseReconnectDelay = 2000 // 基础重连延迟2秒
    const maxReconnectDelay = 30000 // 最大重连延迟30秒
    const heartbeatIntervalTime = 30000 // 30秒
    
    // 计算重连延迟（指数退避）
    const getReconnectDelay = () => {
      const delay = Math.min(baseReconnectDelay * Math.pow(1.5, reconnectAttempts), maxReconnectDelay)
      return Math.floor(delay)
    }
    
    // 创建 WebSocket 连接
    const createWebSocket = () => {
      if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Max reconnect attempts reached')
        setNotification({ message: '实时数据连接重连失败，请刷新页面', type: 'error' })
        return
      }
      
      // 在开发环境连接到后端8000端口，生产环境使用当前主机
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsHost = import.meta.env.DEV 
        ? `${window.location.hostname}:8000` 
        : window.location.host
      socket = new WebSocket(`${wsProtocol}//${wsHost}/ws`)
      
      console.log(`Connecting to WebSocket: ${wsProtocol}//${wsHost}/ws`)
      
      // 连接打开时
      socket.onopen = () => {
        console.log('WebSocket connected')
        setWs(socket) // 更新状态
        setIsConnected(true)
        setNotification({ message: '实时数据连接已建立', type: 'success' })
        reconnectAttempts = 0
        
        // 启动心跳检测
        startHeartbeat()
      }
      
      // 接收消息时
      socket.onmessage = (event) => {
        try {
          if (event.data === 'pong') {
            // 心跳响应，忽略
            return
          }
          const message = JSON.parse(event.data)
          console.log('Received message:', message)
          setLatestData(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      // 连接关闭时
      socket.onclose = (event) => {
        console.log('WebSocket disconnected, code:', event.code, 'reason:', event.reason)
        setWs(null) // 清理状态
        setIsConnected(false)
        
        // 停止心跳检测
        stopHeartbeat()
        
        // 尝试重新连接
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = getReconnectDelay()
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`)
          setNotification({ 
            message: `实时数据连接已断开，${Math.round(delay / 1000)}秒后尝试重连... (${reconnectAttempts + 1}/${maxReconnectAttempts})`, 
            type: 'warning' 
          })
          reconnectAttempts++
          reconnectTimeout = setTimeout(() => {
            createWebSocket()
          }, delay)
        } else {
          setNotification({ message: '实时数据连接重连失败，请刷新页面', type: 'error' })
        }
      }
      
      // 连接错误时
      socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        // 不在这里显示通知，让onclose处理
      }
    }
    
    // 启动心跳检测
    const startHeartbeat = () => {
      stopHeartbeat() // 先停止之前的心跳
      
      heartbeatInterval = setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
          try {
            socket.send('ping') // 发送心跳包
          } catch (error) {
            console.error('Error sending heartbeat:', error)
            // 如果发送失败，可能连接已断开
            if (socket) {
              socket.close()
            }
          }
        }
      }, heartbeatIntervalTime)
    }
    
    // 停止心跳检测
    const stopHeartbeat = () => {
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval)
        heartbeatInterval = null
      }
    }
    
    // 创建初始连接
    createWebSocket()
    
    // 清理函数
    return () => {
      if (socket) {
        socket.close()
      }
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval)
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
    }
  }, [])

  // 发送消息的函数
  const sendMessage = (message: any) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(message))
    }
  }

  // 处理抽屉切换
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  // 处理通知关闭
  const handleNotificationClose = () => {
    setNotification(null)
  }

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          LLMQuant News
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  )

  return (
    <WebSocketContext.Provider value={{ ws, isConnected, latestData, sendMessage }}>
      <Box sx={{ display: 'flex' }}>
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` },
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              AI新闻量化平台
            </Typography>
            <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {isConnected ? '实时连接: 已连接' : '实时连接: 未连接'}
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>
        <Box
          component="nav"
          sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        >
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
        <Box
          component="main"
          sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
        >
          <Toolbar />
          {children}
        </Box>
      </Box>
      <Snackbar
        open={!!notification}
        autoHideDuration={3000}
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        {notification && (
          <Alert
            onClose={handleNotificationClose}
            severity={notification.type}
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        )}
      </Snackbar>
    </WebSocketContext.Provider>
  )
}
