import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
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
} from '@mui/material'
import axios from 'axios'

const API_URL = '/api/v1'

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
  })

  const { data, isLoading } = useQuery({
    queryKey: ['news', page, rowsPerPage, filters],
    queryFn: () =>
      fetchNews({
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        ...filters,
      }),
  })

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

  if (isLoading) {
    return <LinearProgress />
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        新闻列表
      </Typography>

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
