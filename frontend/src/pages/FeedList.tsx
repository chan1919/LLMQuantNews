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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
  Button,
  TextField,
  Divider,
  Paper,
} from '@mui/material';
import {
  TrendingUp as BullishIcon,
  TrendingDown as BearishIcon,
  TrendingFlat as NeutralIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';
import type { NewsFeedItem, PositionBias } from '../types';

const API_URL = '/api/v1';

interface FeedResponse {
  items: NewsFeedItem[];
  total: number;
  has_more: boolean;
}

interface FilterParams {
  keywords?: string[];
  categories?: string[];
  sources?: string[];
  minScore?: number;
  maxScore?: number;
}

const fetchNewsFeed = async (offset: number, limit: number, filters?: FilterParams): Promise<FeedResponse> => {
  const { data } = await axios.get(`${API_URL}/news/feed`, {
    params: { 
      offset, 
      limit,
      ...filters
    }
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
  
  // 从localStorage加载筛选状态
  const loadFiltersFromStorage = (): FilterParams => {
    try {
      const saved = localStorage.getItem('feedFilters');
      return saved ? JSON.parse(saved) : {
        keywords: [],
        categories: [],
        sources: [],
        minScore: 0,
        maxScore: 100,
      };
    } catch (error) {
      console.error('Failed to load filters from storage:', error);
      return {
        keywords: [],
        categories: [],
        sources: [],
        minScore: 0,
        maxScore: 100,
      };
    }
  };

  // 筛选状态
  const [filters, setFilters] = useState<FilterParams>(loadFiltersFromStorage());

  // 保存筛选状态到localStorage
  useEffect(() => {
    localStorage.setItem('feedFilters', JSON.stringify(filters));
  }, [filters]);
  
  // 输入框状态
  const [keywordInput, setKeywordInput] = useState('');
  const [activeFilters, setActiveFilters] = useState<string[]>([]);

  // 模拟数据 - 实际项目中应该从API获取
  const availableCategories = ['科技', '财经', '体育', '娱乐', '政治', '教育', '健康', '汽车'];
  const availableSources = ['新浪财经', '腾讯新闻', '网易新闻', '凤凰网', '新华网'];

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['newsFeed', offset, filters],
    queryFn: () => fetchNewsFeed(offset, limit, filters),
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

  // 当筛选条件变化时重置偏移量
  useEffect(() => {
    setOffset(0);
    setHasMore(true);
  }, [filters]);

  // 计算当前激活的筛选条件
  useEffect(() => {
    const active = [];
    if (filters.keywords && filters.keywords.length > 0) {
      filters.keywords.forEach(keyword => active.push(`关键词: ${keyword}`));
    }
    if (filters.categories && filters.categories.length > 0) {
      filters.categories.forEach(category => active.push(`分类: ${category}`));
    }
    if (filters.sources && filters.sources.length > 0) {
      filters.sources.forEach(source => active.push(`来源: ${source}`));
    }
    if (filters.minScore > 0) {
      active.push(`最低评分: ${filters.minScore}`);
    }
    if (filters.maxScore < 100) {
      active.push(`最高评分: ${filters.maxScore}`);
    }
    setActiveFilters(active);
  }, [filters]);

  // 添加关键词
  const handleAddKeyword = () => {
    if (keywordInput.trim()) {
      setFilters(prev => ({
        ...prev,
        keywords: [...(prev.keywords || []), keywordInput.trim()]
      }));
      setKeywordInput('');
    }
  };

  // 移除关键词
  const handleRemoveKeyword = (keyword: string) => {
    setFilters(prev => ({
      ...prev,
      keywords: prev.keywords?.filter(k => k !== keyword)
    }));
  };

  // 处理分类选择
  const handleCategoryChange = (event: any) => {
    setFilters(prev => ({
      ...prev,
      categories: event.target.value
    }));
  };

  // 处理来源选择
  const handleSourceChange = (event: any) => {
    setFilters(prev => ({
      ...prev,
      sources: event.target.value
    }));
  };

  // 处理评分范围变化
  const handleScoreChange = (type: 'min' | 'max', value: number) => {
    setFilters(prev => ({
      ...prev,
      [type === 'min' ? 'minScore' : 'maxScore']: value
    }));
  };

  // 重置所有筛选
  const handleResetFilters = () => {
    setFilters({
      keywords: [],
      categories: [],
      sources: [],
      minScore: 0,
      maxScore: 100,
    });
  };

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

      {/* 筛选组件 */}
      <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterIcon fontSize="small" />
          筛选条件
        </Typography>

        {/* 关键词输入 */}
        <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="输入关键词"
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            size="small"
          />
          <Button
            variant="contained"
            size="small"
            onClick={handleAddKeyword}
          >
            添加
          </Button>
        </Box>

        {/* 已选关键词 */}
        {filters.keywords && filters.keywords.length > 0 && (
          <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {filters.keywords.map((keyword, index) => (
              <Chip
                key={index}
                label={keyword}
                onDelete={() => handleRemoveKeyword(keyword)}
                size="small"
                sx={{ bgcolor: '#e3f2fd', color: '#1976d2' }}
              />
            ))}
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* 分类和来源选择 */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2, mb: 2 }}>
          {/* 分类选择 */}
          <FormControl fullWidth size="small">
            <InputLabel id="category-select-label">分类</InputLabel>
            <Select
              labelId="category-select-label"
              multiple
              value={filters.categories || []}
              onChange={handleCategoryChange}
              label="分类"
              renderValue={(selected) => selected.join(', ')}
            >
              {availableCategories.map((category) => (
                <MenuItem key={category} value={category}>
                  <Checkbox checked={(filters.categories || []).includes(category)} />
                  <ListItemText primary={category} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* 来源选择 */}
          <FormControl fullWidth size="small">
            <InputLabel id="source-select-label">来源</InputLabel>
            <Select
              labelId="source-select-label"
              multiple
              value={filters.sources || []}
              onChange={handleSourceChange}
              label="来源"
              renderValue={(selected) => selected.join(', ')}
            >
              {availableSources.map((source) => (
                <MenuItem key={source} value={source}>
                  <Checkbox checked={(filters.sources || []).includes(source)} />
                  <ListItemText primary={source} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* 评分范围 */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" sx={{ minWidth: 80 }}>评分范围:</Typography>
          <TextField
            type="number"
            size="small"
            value={filters.minScore}
            onChange={(e) => handleScoreChange('min', parseInt(e.target.value) || 0)}
            InputProps={{ inputProps: { min: 0, max: 100 } }}
            sx={{ width: 80 }}
          />
          <Typography variant="body2">-</Typography>
          <TextField
            type="number"
            size="small"
            value={filters.maxScore}
            onChange={(e) => handleScoreChange('max', parseInt(e.target.value) || 100)}
            InputProps={{ inputProps: { min: 0, max: 100 } }}
            sx={{ width: 80 }}
          />
        </Box>

        {/* 操作按钮 */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleResetFilters}
          >
            重置
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<RefreshIcon fontSize="small" />}
            onClick={() => setOffset(0)}
          >
            应用筛选
          </Button>
        </Box>
      </Paper>

      {/* 激活的筛选条件显示 */}
      {activeFilters.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {activeFilters.map((filter, index) => (
            <Chip key={index} label={filter} size="small" sx={{ bgcolor: '#f5f5f5' }} />
          ))}
        </Box>
      )}

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
