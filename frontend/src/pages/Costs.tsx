import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import axios from 'axios'

const API_URL = '/api/v1'

const fetchCostSummary = async () => {
  const { data } = await axios.get(`${API_URL}/costs/summary`)
  return data
}

const fetchBudgetStatus = async () => {
  const { data } = await axios.get(`${API_URL}/costs/budget`)
  return data
}

export default function Costs() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['costSummary'],
    queryFn: fetchCostSummary,
  })

  const { data: budget, isLoading: budgetLoading } = useQuery({
    queryKey: ['budgetStatus'],
    queryFn: fetchBudgetStatus,
  })

  if (summaryLoading || budgetLoading) {
    return <LinearProgress />
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        成本统计
      </Typography>

      {budget?.status === 'danger' && (
        <Alert severity="error" sx={{ mb: 2 }}>
          本月预算已超支！当前使用: ${budget?.monthly_cost_usd} / ${budget?.budget_usd}
        </Alert>
      )}

      {budget?.status === 'warning' && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          本月预算即将用尽！当前使用: {budget?.percentage}%
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              本月成本 (USD)
            </Typography>
            <Typography variant="h4">
              ${summary?.total_cost_usd?.toFixed(2) || '0.00'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              ¥{summary?.total_cost_cny?.toFixed(2) || '0.00'}
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              总请求数
            </Typography>
            <Typography variant="h4">
              {summary?.total_requests || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {summary?.total_tokens?.toLocaleString() || 0} tokens
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              预算状态
            </Typography>
            <Typography variant="h4">
              {budget?.percentage?.toFixed(1) || 0}%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              ${budget?.remaining?.toFixed(2) || '0.00'} 剩余
            </Typography>
          </CardContent>
        </Card>
      </Box>

      <Typography variant="h6" sx={{ mb: 2 }}>
        按模型统计
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>模型</TableCell>
              <TableCell align="right">请求数</TableCell>
              <TableCell align="right">Tokens</TableCell>
              <TableCell align="right">成本 (USD)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(summary?.by_model || {}).map(([model, data]: [string, any]) => (
              <TableRow key={model}>
                <TableCell>{model}</TableCell>
                <TableCell align="right">{data.requests}</TableCell>
                <TableCell align="right">{data.tokens?.toLocaleString()}</TableCell>
                <TableCell align="right">${data.cost_usd?.toFixed(4)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
