import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Button,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Divider,
  Link,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  TrendingUp as BullishIcon,
  TrendingDown as BearishIcon,
  TrendingFlat as NeutralIcon,
  AccessTime as TimeIcon,
  Language as SourceIcon,
} from '@mui/icons-material';
import axios from 'axios';
import type { NewsDetail, PositionBias, ImpactDimension } from '../types';

const API_URL = '/api/v1';

const fetchNewsDetail = async (newsId: string): Promise<NewsDetail> => {
  const { data } = await axios.get(`${API_URL}/news/${newsId}/detail`);
  return data;
};

const getBiasColor = (bias: PositionBias): string => {
  switch (bias) {
    case 'bullish':
      return '#22c55e';
    case 'bearish':
      return '#ef4444';
    default:
      return '#6b7280';
  }
};

const getBiasIcon = (bias: PositionBias) => {
  switch (bias) {
    case 'bullish':
      return <BullishIcon />;
    case 'bearish':
      return <BearishIcon />;
    default:
      return <NeutralIcon />;
  }
};

const getBiasText = (bias: PositionBias): string => {
  switch (bias) {
    case 'bullish':
      return '利多';
    case 'bearish':
      return '利空';
    default:
      return '中性';
  }
};

const getDimensionName = (dimension: string): string => {
  const names: Record<string, string> = {
    market: '市场影响',
    industry: '行业影响',
    policy: '政策影响',
    tech: '技术影响',
  };
  return names[dimension] || dimension;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

interface ImpactCardProps {
  dimension: string;
  data: ImpactDimension;
  weight: number;
}

function ImpactCard({ dimension, data, weight }: ImpactCardProps) {
  return (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {getDimensionName(dimension)}
          </Typography>
          <Chip
            label={`权重 ${(weight * 100).toFixed(0)}%`}
            size="small"
            variant="outlined"
          />
        </Box>

        {/* 评分条 */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              影响强度
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {data.score.toFixed(1)}分
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={data.score}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: '#e5e7eb',
              '& .MuiLinearProgress-bar': {
                bgcolor: getBiasColor(data.bias),
                borderRadius: 4,
              },
            }}
          />
        </Box>

        {/* 多空标识 */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 2,
            p: 1,
            bgcolor: `${getBiasColor(data.bias)}10`,
            borderRadius: 1,
          }}
        >
          {getBiasIcon(data.bias)}
          <Typography
            variant="body2"
            fontWeight="medium"
            sx={{ color: getBiasColor(data.bias) }}
          >
            {getBiasText(data.bias)} {data.magnitude.toFixed(0)}%
          </Typography>
        </Box>

        {/* 影响分析 */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            lineHeight: 1.6,
            display: '-webkit-box',
            WebkitLineClamp: 4,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {data.analysis}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function NewsDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: news, isLoading } = useQuery({
    queryKey: ['newsDetail', id],
    queryFn: () => fetchNewsDetail(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <LinearProgress sx={{ width: '100%' }} />
      </Box>
    );
  }

  if (!news) {
    return (
      <Box sx={{ textAlign: 'center', p: 4 }}>
        <Typography variant="h6" color="text.secondary">
          未找到新闻
        </Typography>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          返回信息流
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto' }}>
      {/* 返回按钮 */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/')}
        sx={{ mb: 2 }}
      >
        返回信息流
      </Button>

      {/* 标题 */}
      <Typography
        variant="h4"
        sx={{
          fontWeight: 'bold',
          color: '#1a1a1a',
          lineHeight: 1.4,
          mb: 2,
        }}
      >
        {news.title}
      </Typography>

      {/* 元信息 */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          alignItems: 'center',
          flexWrap: 'wrap',
          mb: 3,
        }}
      >
        <Link
          href={news.source_url}
          target="_blank"
          rel="noopener noreferrer"
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            textDecoration: 'none',
          }}
        >
          <SourceIcon fontSize="small" />
          <Typography variant="body2">{news.source}</Typography>
        </Link>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <TimeIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {formatDate(news.published_at)}
          </Typography>
        </Box>

        {news.author && (
          <Typography variant="body2" color="text.secondary">
            作者：{news.author}
          </Typography>
        )}
      </Box>

      {/* 评分概览卡片 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="overline" color="text.secondary">
                综合评分
              </Typography>
              <Typography
                variant="h2"
                fontWeight="bold"
                sx={{
                  color: news.final_score >= 70 ? '#ef4444' :
                         news.final_score >= 50 ? '#f59e0b' :
                         news.final_score >= 30 ? '#22c55e' : '#6b7280'
                }}
              >
                {news.final_score.toFixed(1)}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="overline" color="text.secondary">
                多空判断
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 1,
                  mt: 1,
                }}
              >
                {getBiasIcon(news.position_bias)}
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  sx={{ color: getBiasColor(news.position_bias) }}
                >
                  {getBiasText(news.position_bias)}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                幅度 {news.position_magnitude.toFixed(0)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="overline" color="text.secondary">
                情绪倾向
              </Typography>
              <Typography
                variant="h5"
                fontWeight="bold"
                sx={{
                  color: news.sentiment === 'positive' ? '#22c55e' :
                         news.sentiment === 'negative' ? '#ef4444' : '#6b7280',
                  mt: 1,
                }}
              >
                {news.sentiment === 'positive' ? '积极' :
                 news.sentiment === 'negative' ? '消极' : '中性'}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* 多维度影响分析 */}
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
        多维度影响分析
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {Object.entries(news.impact_analysis).map(([dimension, data]) => (
          <Grid item xs={12} sm={6} key={dimension}>
            <ImpactCard
              dimension={dimension}
              data={data}
              weight={news.relevance_weights[dimension] || 0.25}
            />
          </Grid>
        ))}
      </Grid>

      {/* 关键词和分类 */}
      <Box sx={{ mb: 3 }}>
        {news.keywords.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              关键词
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {news.keywords.map((keyword) => (
                <Chip key={keyword} label={keyword} size="small" />
              ))}
            </Box>
          </Box>
        )}

        {news.categories.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              分类
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {news.categories.map((category) => (
                <Chip
                  key={category}
                  label={category}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* 完整内容 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          详细内容
        </Typography>

        {news.summary && (
          <Box
            sx={{
              mb: 3,
              p: 2,
              bgcolor: '#f9fafb',
              borderRadius: 1,
              borderLeft: '4px solid #667eea',
            }}
          >
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              AI摘要
            </Typography>
            <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
              {news.summary}
            </Typography>
          </Box>
        )}

        <Typography
          variant="body1"
          sx={{
            lineHeight: 1.8,
            whiteSpace: 'pre-wrap',
            color: '#374151',
          }}
        >
          {news.content || '暂无内容'}
        </Typography>

        <Box sx={{ mt: 3 }}>
          <Link
            href={news.url}
            target="_blank"
            rel="noopener noreferrer"
            variant="button"
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 0.5,
              textDecoration: 'none',
            }}
          >
            阅读原文 →
          </Link>
        </Box>
      </Paper>
    </Box>
  );
}
