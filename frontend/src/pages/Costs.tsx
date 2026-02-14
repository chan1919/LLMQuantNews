import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  LinearProgress,
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

export default function Costs() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['costSummary'],
    queryFn: fetchCostSummary,
  })

  if (summaryLoading) {
    return <LinearProgress />
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        使用统计
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              总请求数
            </Typography>
            <Typography variant="h4">
              {summary?.total_requests || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              次API调用
            </Typography>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              总Token消耗
            </Typography>
            <Typography variant="h4">
              {summary?.total_tokens?.toLocaleString() || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Tokens
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
              <TableCell align="right">总Tokens</TableCell>
              <TableCell align="right">输入Tokens</TableCell>
              <TableCell align="right">输出Tokens</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(summary?.by_model || {}).map(([model, data]: [string, any]) => (
              <TableRow key={model}>
                <TableCell>{model}</TableCell>
                <TableCell align="right">{data.requests}</TableCell>
                <TableCell align="right">{data.tokens?.toLocaleString()}</TableCell>
                <TableCell align="right">{data.prompt_tokens?.toLocaleString()}</TableCell>
                <TableCell align="right">{data.completion_tokens?.toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
