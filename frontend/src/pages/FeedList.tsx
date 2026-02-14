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

const fetchTags = async (): Promise<string[]> => {
  const { data } = await axios.get(`${API_URL}/news/tags/list`);
  return data.tags || [];
};

const searchNews = async (query: string, skip: number = 0, limit: number = 20): Promise<FeedResponse> => {
  const { data } = await axios.get(`${API_URL}/news/search`, {
    params: { query, skip, limit }
  });
  return {
    items: data.items || [],
    total: data.total || 0,
    has_more: (skip + limit) < (data.total || 0)
  };
};

const searchByTags = async (tags: string[], skip: number = 0, limit: number = 20): Promise<FeedResponse> => {
  const { data } = await axios.get(`${API_URL}/news/tags/search`, {
    params: { tags, skip, limit }
  });
  return {
    items: data.items || [],
    total: data.total || 0,
    has_more: (skip + limit) < (data.total || 0)
  };
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
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // 获取可用标签
  const { data: tagsData, isLoading: tagsLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: fetchTags,
    staleTime: 5 * 60 * 1000, // 5分钟缓存
  });

  // 更新可用标签
  useEffect(() => {
    if (tagsData) {
      setAvailableTags(tagsData);
    }
  }, [tagsData]);

  // 模拟数据 - 实际项目中应该从API获取
  const availableCategories = ['科技', '财经', '体育', '娱乐', '政治', '教育', '健康', '汽车'];
  const availableSources = ['新浪财经', '腾讯新闻', '网易新闻', '凤凰网', '新华网'];

  // 基础新闻Feed查询
  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['newsFeed', offset, filters],
    queryFn: () => fetchNewsFeed(offset, limit, filters),
    enabled: hasMore && !isSearchMode,
  });

  // 搜索查询
  const { data: searchData, isLoading: searchLoading, isFetching: searchFetching } = useQuery({
    queryKey: ['searchNews', searchQuery, offset],
    queryFn: () => searchNews(searchQuery, offset, limit),
    enabled: isSearchMode && searchQuery.trim().length > 0,
  });

  // 当数据加载时追加到列表
  useEffect(() => {
    if (data && !isSearchMode) {
      if (offset === 0) {
        setItems(data.items);
      } else {
        setItems(prev => [...prev, ...data.items]);
      }
      setHasMore(data.has_more);
    }
  }, [data, offset, isSearchMode]);

  // 当搜索结果加载时
  useEffect(() => {
    if (searchData && isSearchMode) {
      if (offset === 0) {
        setItems(searchData.items);
      } else {
        setItems(prev => [...prev, ...searchData.items]);
      }
      setHasMore(searchData.has_more);
    }
  }, [searchData, offset, isSearchMode]);

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

  // 预设关键词组
  const predefinedKeywords = {
    '科技': ['人工智能', '机器学习', '区块链', '元宇宙', '云计算', '大数据'],
    '财经': ['股票市场', '数字货币', '通货膨胀', '利率', '经济增长', '投资策略'],
    '政策': ['监管政策', '法律法规', '行业政策', '税收政策', '补贴政策'],
    '市场': ['市场趋势', '竞争格局', '消费者行为', '商业模式', '技术创新']
  };

  // 添加关键词
  const handleAddKeyword = () => {
    if (keywordInput.trim()) {
      setFilters(prev => {
        const currentKeywords = prev.keywords || [];
        if (!currentKeywords.includes(keywordInput.trim())) {
          return {
            ...prev,
            keywords: [...currentKeywords, keywordInput.trim()]
          };
        }
        return prev;
      });
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

  // 批量添加关键词组
  const handleAddKeywordGroup = (group: string[]) => {
    setFilters(prev => {
      const currentKeywords = prev.keywords || [];
      const newKeywords = group.filter(keyword => !currentKeywords.includes(keyword));
      return {
        ...prev,
        keywords: [...currentKeywords, ...newKeywords]
      };
    });
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

  // 处理搜索提交
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setIsSearchMode(true);
      setOffset(0);
      setHasMore(true);
    }
  };

  // 切换回筛选模式
  const handleSwitchToFilterMode = () => {
    setIsSearchMode(false);
    setSearchQuery('');
    setOffset(0);
    setHasMore(true);
  };

  // 处理标签选择
  const handleTagToggle = (tag: string) => {
    setFilters(prev => {
      const currentTags = prev.keywords || [];
      if (currentTags.includes(tag)) {
        return {
          ...prev,
          keywords: currentTags.filter(t => t !== tag)
        };
      } else {
        return {
          ...prev,
          keywords: [...currentTags, tag]
        };
      }
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

  // 移除初始加载的转圈动画，实现无感刷新
  if (isLoading && items.length === 0) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          加载中...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        信息流
      </Typography>

      {/* 紧凑搜索和筛选组件 */}
      <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* 第一行：搜索框和模式切换 */}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder={isSearchMode ? "输入搜索查询" : "输入关键词或搜索查询"}
            value={isSearchMode ? searchQuery : keywordInput}
            onChange={(e) => isSearchMode ? setSearchQuery(e.target.value) : setKeywordInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                if (isSearchMode) {
                  handleSearchSubmit(e);
                } else {
                  handleAddKeyword();
                }
              }
            }}
            size="small"
            sx={{ flex: 1 }}
          />
          {isSearchMode ? (
            <>
              <Button
                type="submit"
                variant="contained"
                size="small"
                onClick={(e) => handleSearchSubmit(e)}
              >
                搜索
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={handleSwitchToFilterMode}
              >
                筛选
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="contained"
                size="small"
                onClick={handleAddKeyword}
              >
                添加
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={(e) => handleSearchSubmit(e)}
              >
                搜索
              </Button>
            </>
          )}
        </Box>

        {/* 第二行：快速筛选选项 */}
        {!isSearchMode && (
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            {/* 分类选择 */}
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="category-select-label">分类</InputLabel>
              <Select
                labelId="category-select-label"
                multiple
                value={filters.categories || []}
                onChange={handleCategoryChange}
                label="分类"
                renderValue={(selected) => selected.join(', ')}
                size="small"
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
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="source-select-label">来源</InputLabel>
              <Select
                labelId="source-select-label"
                multiple
                value={filters.sources || []}
                onChange={handleSourceChange}
                label="来源"
                renderValue={(selected) => selected.join(', ')}
                size="small"
              >
                {availableSources.map((source) => (
                  <MenuItem key={source} value={source}>
                    <Checkbox checked={(filters.sources || []).includes(source)} />
                    <ListItemText primary={source} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* 关键词组选择 */}
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel id="keyword-group-label">关键词组</InputLabel>
              <Select
                labelId="keyword-group-label"
                value=""
                onChange={(e) => {
                  const groupName = e.target.value;
                  if (groupName && predefinedKeywords[groupName]) {
                    handleAddKeywordGroup(predefinedKeywords[groupName]);
                  }
                }}
                label="关键词组"
                size="small"
              >
                {Object.keys(predefinedKeywords).map((group) => (
                  <MenuItem key={group} value={group}>
                    <ListItemText primary={group} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* 评分范围 */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>评分:</Typography>
              <TextField
                type="number"
                size="small"
                value={filters.minScore}
                onChange={(e) => handleScoreChange('min', parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 0, max: 100 } }}
                sx={{ width: 60 }}
              />
              <Typography variant="body2">-</Typography>
              <TextField
                type="number"
                size="small"
                value={filters.maxScore}
                onChange={(e) => handleScoreChange('max', parseInt(e.target.value) || 100)}
                InputProps={{ inputProps: { min: 0, max: 100 } }}
                sx={{ width: 60 }}
              />
            </Box>

            {/* 操作按钮 */}
            <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
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
                onClick={() => setOffset(0)}
              >
                应用
              </Button>
            </Box>
          </Box>
        )}
      </Box>

      {/* 已选关键词（带删除功能） */}
      {!isSearchMode && filters.keywords && filters.keywords.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
            已选关键词:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {filters.keywords.map((keyword, index) => (
              <Chip
                key={index}
                label={keyword}
                onDelete={() => handleRemoveKeyword(keyword)}
                color="primary"
                variant="filled"
                size="small"
                sx={{ bgcolor: '#e3f2fd', color: '#1976d2' }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* AI标签选择（紧凑版） */}
      {!isSearchMode && availableTags.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
            AI标签:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, maxHeight: 80, overflowY: 'auto' }}>
            {availableTags.slice(0, 15).map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onClick={() => handleTagToggle(tag)}
                color={filters.keywords?.includes(tag) ? 'primary' : 'default'}
                variant={filters.keywords?.includes(tag) ? 'filled' : 'outlined'}
                size="small"
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* 已选条件显示 */}
      {activeFilters.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
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

                  {/* AI评分 */}
                  <Chip
                    label={`AI: ${news.ai_score.toFixed(1)}`}
                    color="primary"
                    size="small"
                    variant="outlined"
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

                  {/* 情感标签 */}
                  <Chip
                    label={news.sentiment === 'positive' ? '积极' : 
                           news.sentiment === 'negative' ? '消极' : '中性'}
                    size="small"
                    sx={{
                      bgcolor: news.sentiment === 'positive' ? '#22c55e20' : 
                               news.sentiment === 'negative' ? '#ef444420' : '#6b728020',
                      color: news.sentiment === 'positive' ? '#22c55e' : 
                             news.sentiment === 'negative' ? '#ef4444' : '#6b7280',
                      fontWeight: 'medium',
                    }}
                  />

                  {/* 分析状态 */}
                  <Chip
                    label={news.is_analyzed ? '已分析' : '未分析'}
                    size="small"
                    sx={{
                      bgcolor: news.is_analyzed ? '#10b98120' : '#f59e0b20',
                      color: news.is_analyzed ? '#10b981' : '#f59e0b',
                      fontWeight: 'medium',
                    }}
                  />

                  {/* 时间 */}
                  <Typography variant="caption" color="text.secondary">
                    {news.time_ago}
                  </Typography>
                </Box>

                {/* AI分析指标 */}
                {news.is_analyzed && (
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 1,
                      flexWrap: 'wrap',
                      mb: 1.5,
                    }}
                  >
                    {/* 市场影响度 */}
                    <Chip
                      label={`市场: ${news.market_impact.toFixed(0)}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />

                    {/* 行业相关性 */}
                    <Chip
                      label={`行业: ${news.industry_relevance.toFixed(0)}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />

                    {/* 信息新颖度 */}
                    <Chip
                      label={`新颖: ${news.novelty_score.toFixed(0)}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />

                    {/* 紧急程度 */}
                    <Chip
                      label={`紧急: ${news.urgency.toFixed(0)}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.75rem' }}
                    />
                  </Box>
                )}

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

      {/* 隐藏加载更多指示器，实现无感刷新 */}
      {/* {isFetching && (
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
