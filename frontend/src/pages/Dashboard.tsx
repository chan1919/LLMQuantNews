import { useQuery } from '@tanstack/react-query'
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  LinearProgress,
} from '@mui/material'
import {
  Article as ArticleIcon,
  TrendingUp as TrendingIcon,
  AttachMoney as MoneyIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import axios from 'axios'

const API_URL = '/api/v1'

const fetchDashboardStats = async () => {
  const { data } = await axios.get(`${API_URL}/dashboard/stats`)
  return data
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: fetchDashboardStats,
  })

  if (isLoading) {
    return <LinearProgress />
  }

  const statCards = [
    {
      title: '总新闻数',
      value: stats?.total_news || 0,
      subValue: `今日: ${stats?.today_news || 0}`,
      icon: <ArticleIcon />,
      color: '#667eea',
    },
    {
      title: '已推送',
      value: stats?.total_pushed || 0,
      subValue: `今日: ${stats?.today_pushed || 0}`,
      icon: <TrendingIcon />,
      color: '#764ba2',
    },
    {
      title: '月度成本',
      value: `$${(stats?.monthly_cost_usd || 0).toFixed(2)}`,
      subValue: `总成本: $${(stats?.total_cost_usd || 0).toFixed(2)}`,
      icon: <MoneyIcon />,
      color: '#f093fb',
    },
    {
      title: '活跃爬虫',
      value: stats?.active_crawlers || 0,
      subValue: `平均分: ${(stats?.avg_score || 0).toFixed(1)}`,
      icon: <SettingsIcon />,
      color: '#4facfe',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4 }}>
        仪表盘
      </Typography>
      
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
        最近新闻
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        {stats?.recent_news?.map((news: any) => (
          <Box key={news.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
            <Typography variant="h6">{news.title}</Typography>
            <Typography variant="body2" color="textSecondary">
              来源: {news.source} | 评分: {news.final_score} | 
              {new Date(news.crawled_at).toLocaleString()}
            </Typography>
          </Box>
        ))}
      </Paper>
    </Box>
  )
}
