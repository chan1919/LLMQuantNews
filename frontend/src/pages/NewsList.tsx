import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  LinearProgress,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Tooltip,
  Badge,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material'
import axios from 'axios'
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

const fetchNews = async (params: any) => {
  const { data } = await axios.get(`${API_URL}/news`, { params })
  return data
}

export default function NewsList() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(20)
  const [filters, setFilters] = useState({
    keyword: '',
    source: '',
    min_score: '',
    date: '',
  })
  const [dates] = useState<Date[]>(generateRecentDates())
  const [autoRefresh, setAutoRefresh] = useState(false) // 默认关闭自动刷新
  const [newDataCount, setNewDataCount] = useState(0) // 新数据计数
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const queryClient = useQueryClient()
  const { latestData, isConnected } = useWebSocket()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['news', page, rowsPerPage, filters],
    queryFn: () =>
      fetchNews({
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        ...filters,
      }),
  })

  // 防抖刷新函数
  const debouncedRefresh = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current)
    }
    
    refreshTimeoutRef.current = setTimeout(() => {
      queryClient.invalidateQueries({ queryKey: ['news'] })
      setNewDataCount(0)
    }, 5000) // 5秒防抖
  }, [queryClient])

  // 手动刷新
  const handleManualRefresh = () => {
    refetch()
    setNewDataCount(0)
  }

  // 当接收到 WebSocket 消息时，处理新数据通知
  useEffect(() => {
    if (latestData && latestData.type === 'dashboard_update') {
      // 如果当前没有按日期过滤，或者过滤的是今天
      if (!filters.date || filters.date === formatDate(new Date())) {
        if (autoRefresh) {
          // 自动刷新模式：使用防抖刷新
          debouncedRefresh()
        } else {
          // 手动模式：增加新数据计数
          setNewDataCount(prev => prev + 1)
        }
      }
    }
  }, [latestData, filters.date, autoRefresh, debouncedRefresh])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
      }
    }
  }, [])

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'error'
    if (score >= 70) return 'warning'
    return 'default'
  }

  // 处理日期选择
  const handleDateChange = (event: React.SyntheticEvent, newValue: number) => {
    const selectedDate = dates[newValue]
    setFilters({ ...filters, date: formatDate(selectedDate) })
    setPage(0)
  }

  // 清除日期过滤
  const clearDateFilter = () => {
    setFilters({ ...filters, date: '' })
    setPage(0)
  }

  if (isLoading) {
    return <LinearProgress />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          新闻列表
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="自动刷新"
          />
          <Tooltip title={newDataCount > 0 ? `有 ${newDataCount} 条新数据` : '手动刷新'}>
            <Badge badgeContent={newDataCount} color="error">
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={handleManualRefresh}
                disabled={isLoading}
              >
                刷新
              </Button>
            </Badge>
          </Tooltip>
        </Box>
      </Box>

      {/* 日期过滤条 */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
          按日期过滤:
        </Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Tabs
            value={filters.date ? dates.findIndex(date => formatDate(date) === filters.date) : -1}
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
                  py: 1,
                }}
              />
            ))}
          </Tabs>
        </Box>
        {filters.date && (
          <Button 
            variant="outlined" 
            size="small" 
            onClick={clearDateFilter}
            sx={{ mt: 1 }}
          >
            清除日期过滤
          </Button>
        )}
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            label="关键词"
            value={filters.keyword}
            onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
            size="small"
          />
          <TextField
            label="来源"
            value={filters.source}
            onChange={(e) => setFilters({ ...filters, source: e.target.value })}
            size="small"
          />
          <TextField
            label="最低分数"
            type="number"
            value={filters.min_score}
            onChange={(e) => setFilters({ ...filters, min_score: e.target.value })}
            size="small"
          />
          <Button
            variant="contained"
            onClick={() => {
              setPage(0)
            }}
          >
            搜索
          </Button>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>标题</TableCell>
              <TableCell>来源</TableCell>
              <TableCell>分类</TableCell>
              <TableCell>分数</TableCell>
              <TableCell>时间</TableCell>
              <TableCell>状态</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.items?.map((news: any) => (
              <TableRow key={news.id}>
                <TableCell>
                  <a
                    href={news.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ textDecoration: 'none', color: 'inherit' }}
                  >
                    {news.title}
                  </a>
                </TableCell>
                <TableCell>{news.source}</TableCell>
                <TableCell>
                  {news.categories?.map((cat: string) => (
                    <Chip key={cat} label={cat} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <Chip
                    label={news.final_score}
                    color={getScoreColor(news.final_score) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(news.crawled_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {news.is_pushed ? (
                    <Chip label="已推送" color="success" size="small" />
                  ) : (
                    <Chip label="未推送" size="small" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={data?.total || 0}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 20, 50, 100]}
        />
      </TableContainer>
    </Box>
  )
}
