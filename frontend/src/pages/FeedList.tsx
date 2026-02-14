import { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  CircularProgress,
  Link,
  Fade,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp as BullishIcon,
  TrendingDown as BearishIcon,
  TrendingFlat as NeutralIcon,
} from '@mui/icons-material';
import axios from 'axios';
import type { NewsFeedItem, PositionBias } from '../types';

const API_URL = '/api/v1';

interface FeedResponse {
  items: NewsFeedItem[];
  total: number;
  has_more: boolean;
}

const fetchNewsFeed = async (offset: number, limit: number): Promise<FeedResponse> => {
  const { data } = await axios.get(`${API_URL}/news/feed`, {
    params: { offset, limit }
  });
  return data;
};

const getScoreColor = (score: number): 'error' | 'warning' | 'success' | 'default' => {
  if (score >= 70) return 'error';
  if (score >= 50) return 'warning';
  if (score >= 30) return 'success';
  return 'default';
};

const getBiasColor = (bias: PositionBias): string => {
  switch (bias) {
    case 'bullish':
      return '#22c55e';  // 绿色
    case 'bearish':
      return '#ef4444';  // 红色
    default:
      return '#6b7280';  // 灰色
  }
};

const getBiasIcon = (bias: PositionBias) => {
  switch (bias) {
    case 'bullish':
      return <BullishIcon sx={{ fontSize: 16 }} />;
    case 'bearish':
      return <BearishIcon sx={{ fontSize: 16 }} />;
    default:
      return <NeutralIcon sx={{ fontSize: 16 }} />;
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

export default function FeedList() {
  const navigate = useNavigate();
  const [items, setItems] = useState<NewsFeedItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const limit = 20;

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['newsFeed', offset],
    queryFn: () => fetchNewsFeed(offset, limit),
    enabled: hasMore,
  });

  // 当数据加载时追加到列表
  useEffect(() => {
    if (data) {
      if (offset === 0) {
        setItems(data.items);
      } else {
        setItems(prev => [...prev, ...data.items]);
      }
      setHasMore(data.has_more);
    }
  }, [data, offset]);

  // 无限滚动观察器
  const lastElementRef = useCallback((node: HTMLDivElement | null) => {
    if (isFetching) return;
    
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !isFetching) {
        setOffset(prev => prev + limit);
      }
    });

    if (node) {
      observerRef.current.observe(node);
    }
  }, [isFetching, hasMore]);

  const handleNewsClick = (newsId: number) => {
    navigate(`/news/${newsId}`);
  };

  if (isLoading && items.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        信息流
      </Typography>

      {/* 信息列表 */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.map((news, index) => (
          <Fade in key={news.id} timeout={300}>
            <Card
              ref={index === items.length - 1 ? lastElementRef : null}
              sx={{
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  boxShadow: 4,
                  transform: 'translateY(-2px)',
                },
              }}
              onClick={() => handleNewsClick(news.id)}
            >
              <CardContent sx={{ pb: 2 }}>
                {/* 标题 */}
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 'bold',
                    color: '#1a1a1a',
                    lineHeight: 1.4,
                    mb: 1.5,
                  }}
                >
                  {news.title}
                </Typography>

                {/* 简短摘要 */}
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    mb: 2,
                    lineHeight: 1.6,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {news.brief_summary || '暂无摘要'}
                </Typography>

                {/* 影响指标行 */}
                <Box
                  sx={{
                    display: 'flex',
                    gap: 1.5,
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    mb: 1.5,
                  }}
                >
                  {/* 衰减后评分 */}
                  <Chip
                    label={`${news.decayed_score.toFixed(1)}分`}
                    color={getScoreColor(news.decayed_score)}
                    size="small"
                    sx={{ fontWeight: 'medium' }}
                  />

                  {/* 多空标签 */}
                  <Chip
                    icon={getBiasIcon(news.position_bias)}
                    label={`${getBiasText(news.position_bias)} ${news.position_magnitude.toFixed(0)}%`}
                    size="small"
                    sx={{
                      bgcolor: `${getBiasColor(news.position_bias)}20`,
                      color: getBiasColor(news.position_bias),
                      fontWeight: 'medium',
                      '& .MuiChip-icon': {
                        color: getBiasColor(news.position_bias),
                      },
                    }}
                  />

                  {/* 时间 */}
                  <Typography variant="caption" color="text.secondary">
                    {news.time_ago}
                  </Typography>
                </Box>

                {/* 简短影响描述 */}
                <Typography
                  variant="body2"
                  sx={{
                    fontStyle: 'italic',
                    color: getBiasColor(news.position_bias),
                    mb: 1.5,
                    lineHeight: 1.5,
                  }}
                >
                  影响：{news.brief_impact || '暂无影响分析'}
                </Typography>

                {/* 来源链接 */}
                <Link
                  href={news.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  variant="caption"
                  color="primary"
                  onClick={(e) => e.stopPropagation()}
                  sx={{
                    textDecoration: 'none',
                    '&:hover': { textDecoration: 'underline' },
                  }}
                >
                  来源：{news.source} →
                </Link>
              </CardContent>
            </Card>
          </Fade>
        ))}
      </Box>

      {/* 加载更多指示器 */}
      {isFetching && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
        </Box>
      )}

      {/* 没有更多数据 */}
      {!hasMore && items.length > 0 && (
        <Typography
          variant="body2"
          color="text.secondary"
          align="center"
          sx={{ mt: 4, mb: 2 }}
        >
          已加载全部内容
        </Typography>
      )}

      {/* 空状态 */}
      {!isLoading && items.length === 0 && (
        <Typography
          variant="body1"
          color="text.secondary"
          align="center"
          sx={{ mt: 8 }}
        >
          暂无新闻数据
        </Typography>
      )}
    </Box>
  );
}
