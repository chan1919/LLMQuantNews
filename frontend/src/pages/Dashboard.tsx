import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  LinearProgress,
  Chip,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Article as ArticleIcon,
  TrendingUp as TrendingIcon,
  AttachMoney as MoneyIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { useState, useEffect } from 'react'
import { useWebSocket } from '../components/Layout'

const API_URL = '/api/v1'

// 生成最近7天的日期
const generateRecentDates = () => {
  const dates = []
  const today = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    dates.push(date)
  }
  
  return dates
}

// 格式化日期为 YYYY-MM-DD
const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

// 格式化日期为显示格式
const formatDisplayDate = (date: Date) => {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
}

const fetchDashboardStats = async (date?: string) => {
  const params = date ? { date } : {}
  const { data } = await axios.get(`${API_URL}/dashboard/stats`, { params })
  return data
}

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [dates, setDates] = useState<Date[]>(generateRecentDates())
  const [localStats, setLocalStats] = useState<any>(null)
  const queryClient = useQueryClient()
  const { latestData, isConnected } = useWebSocket()

  // 使用 useQuery 获取初始数据
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboardStats', formatDate(selectedDate)],
    queryFn: () => fetchDashboardStats(formatDate(selectedDate)),
  })

  // 当获取到初始数据时，更新本地状态
  useEffect(() => {
    if (stats) {
      setLocalStats(stats)
    }
  }, [stats])

  // 当接收到 WebSocket 消息时，更新本地状态
  useEffect(() => {
    if (latestData && latestData.type === 'dashboard_update') {
      // 只更新当天的数据
      if (formatDate(selectedDate) === formatDate(new Date())) {
        setLocalStats(prevStats => ({
          ...prevStats,
          today_news: latestData.data.today_news,
          today_pushed: latestData.data.today_pushed,
          recent_news: latestData.data.recent_news
        }))
      }
    }
  }, [latestData, selectedDate])

  // 处理日期选择
  const handleDateChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedDate(dates[newValue])
  }

  if (isLoading) {
    return <LinearProgress />
  }

  // 使用本地状态或查询数据
  const displayStats = localStats || stats

  const statCards = [
    {
      title: '总新闻数',
      value: displayStats?.total_news || 0,
      subValue: `${formatDisplayDate(selectedDate)}: ${displayStats?.today_news || 0}`,
      icon: <ArticleIcon />,
      color: '#667eea',
    },
    {
      title: '已推送',
      value: displayStats?.total_pushed || 0,
      subValue: `${formatDisplayDate(selectedDate)}: ${displayStats?.today_pushed || 0}`,
      icon: <TrendingIcon />,
      color: '#764ba2',
    },
    {
      title: '月度成本',
      value: `$${(displayStats?.monthly_cost_usd || 0).toFixed(2)}`,
      subValue: `总成本: $${(displayStats?.total_cost_usd || 0).toFixed(2)}`,
      icon: <MoneyIcon />,
      color: '#f093fb',
    },
    {
      title: '活跃爬虫',
      value: displayStats?.active_crawlers || 0,
      subValue: `平均分: ${(displayStats?.avg_score || 0).toFixed(1)}`,
      icon: <SettingsIcon />,
      color: '#4facfe',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        仪表盘
      </Typography>

      {/* 日期滑动条 */}
      <Box sx={{ mb: 4, overflowX: 'auto' }}>
        <Tabs
          value={dates.findIndex(date => date.toDateString() === selectedDate.toDateString())}
          onChange={handleDateChange}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
          sx={{
            '& .MuiTabs-indicator': {
              backgroundColor: '#667eea',
            },
            '& .Mui-selected': {
              color: '#667eea !important',
              fontWeight: 'bold',
            },
          }}
        >
          {dates.map((date, index) => (
            <Tab 
              key={index} 
              label={formatDisplayDate(date)}
              sx={{
                minWidth: '80px',
                py: 2,
              }}
            />
          ))}
        </Tabs>
      </Box>
      
      <Grid container spacing={3}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 2,
                      bgcolor: card.color,
                      color: 'white',
                      mr: 2,
                    }}
                  >
                    {card.icon}
                  </Box>
                  <Typography color="textSecondary" variant="body2">
                    {card.title}
                  </Typography>
                </Box>
                <Typography variant="h4" component="div">
                  {card.value}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {card.subValue}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        {formatDisplayDate(selectedDate)}的新闻
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        {displayStats?.recent_news?.length > 0 ? (
          displayStats.recent_news.map((news: any) => (
            <Box key={news.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
              <Typography variant="h6">{news.title}</Typography>
              <Typography variant="body2" color="textSecondary">
                来源: {news.source} | 评分: {news.final_score} | 
                {new Date(news.crawled_at).toLocaleString()}
              </Typography>
            </Box>
          ))
        ) : (
          <Typography variant="body2" color="textSecondary">
            该日期没有新闻
          </Typography>
        )}
      </Paper>
    </Box>
  )
}
