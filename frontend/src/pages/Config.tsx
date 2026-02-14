import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Chip,
  Slider,
  Grid,
  MenuItem,
  Card,
  CardContent,
  Select,
  InputLabel,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  Divider,
  FormControl,
} from '@mui/material';
import {
  TrendingUp as BullishIcon,
  TrendingDown as BearishIcon,
  WbSunny as SunIcon,
  Globe as GlobeIcon,
  DeveloperMode as TechIcon,
  CheckCircle as ValidIcon,
  Cancel as InvalidIcon,
  HelpOutline as UnknownIcon,
  Refresh as TestIcon,
  Remove as NeutralIcon,
} from '@mui/icons-material';
import axios from 'axios';
import type { UserConfig, TimeFrame } from '../types';

const API_URL = '/api/v1';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const fetchConfig = async (): Promise<UserConfig> => {
  const { data } = await axios.get(`${API_URL}/config/user`);
  return data;
};

const saveConfig = async (config: Partial<UserConfig>): Promise<UserConfig> => {
  const { data } = await axios.put(`${API_URL}/config/user`, config);
  return data;
};

const fetchCrawlers = async (): Promise<any[]> => {
  const { data } = await axios.get(`${API_URL}/config/crawlers`);
  return data;
};

const fetchVAPIModels = async (): Promise<any[]> => {
  const { data } = await axios.get(`${API_URL}/ai/vapi/models`);
  return data.models;
};

const updateCrawler = async (crawlerId: number, data: any): Promise<any> => {
  const { data: updated } = await axios.put(`${API_URL}/config/crawlers/${crawlerId}`, data);
  return updated;
};

const testCrawler = async (crawlerId: number): Promise<any> => {
  const { data } = await axios.post(`${API_URL}/config/crawlers/${crawlerId}/test`);
  return data;
};

const testAllCrawlers = async (): Promise<any> => {
  const { data } = await axios.post(`${API_URL}/config/crawlers/test-all`);
  return data;
};

export default function Config() {
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [testingCrawlerId, setTestingCrawlerId] = useState<number | null>(null);
  const [testingAll, setTestingAll] = useState(false);

  const { data: configData, isLoading } = useQuery({
    queryKey: ['userConfig'],
    queryFn: fetchConfig,
  });

  const { data: crawlers = [], isLoading: isLoadingCrawlers } = useQuery({
    queryKey: ['crawlers'],
    queryFn: fetchCrawlers,
  });

  const { data: vapiModels = [], isLoading: isLoadingVAPIModels } = useQuery({
    queryKey: ['vapiModels'],
    queryFn: fetchVAPIModels,
  });

  const [selectedVAPIModels, setSelectedVAPIModels] = useState<string[]>([]);

  const crawlerMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => updateCrawler(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crawlers'] });
      setSnackbar({ open: true, message: '配置更新成功', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: '配置更新失败', severity: 'error' });
    },
  });

  const testCrawlerMutation = useMutation({
    mutationFn: testCrawler,
    onMutate: (crawlerId) => {
      setTestingCrawlerId(crawlerId);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['crawlers'] });
      setSnackbar({ open: true, message: `测试完成: ${data.name} - ${data.is_valid ? '有效' : '无效'}`, severity: data.is_valid ? 'success' : 'error' });
      setTestingCrawlerId(null);
    },
    onError: () => {
      setSnackbar({ open: true, message: '测试失败', severity: 'error' });
      setTestingCrawlerId(null);
    },
  });

  const testAllCrawlersMutation = useMutation({
    mutationFn: testAllCrawlers,
    onMutate: () => {
      setTestingAll(true);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['crawlers'] });
      const validCount = data.results.filter((r: any) => r.is_valid).length;
      setSnackbar({ open: true, message: `批量测试完成: ${validCount}/${data.total} 个信息源有效`, severity: 'success' });
      setTestingAll(false);
    },
    onError: () => {
      setSnackbar({ open: true, message: '批量测试失败', severity: 'error' });
      setTestingAll(false);
    },
  });

  const mutation = useMutation({
    mutationFn: saveConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userConfig'] });
      setSnackbar({ open: true, message: '保存成功', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: '保存失败', severity: 'error' });
    },
  });

  const handleToggleCrawler = (crawlerId: number, isActive: boolean) => {
    crawlerMutation.mutate({ id: crawlerId, data: { is_active: isActive } });
  };

  const handleTestCrawler = (crawlerId: number) => {
    testCrawlerMutation.mutate(crawlerId);
  };

  const handleTestAllCrawlers = () => {
    testAllCrawlersMutation.mutate();
  };

  const getValidityStatus = (crawler: any) => {
    if (crawler.is_valid === true) {
      return { color: 'success', icon: ValidIcon, label: '有效' };
    } else if (crawler.is_valid === false) {
      return { color: 'error', icon: InvalidIcon, label: '无效' };
    } else {
      return { color: 'warning', icon: UnknownIcon, label: '未测试' };
    }
  };

  const [keywords, setKeywords] = useState<Record<string, number>>({});
  const [industries, setIndustries] = useState<string[]>([]);
  const [newIndustry, setNewIndustry] = useState('');
  const [keywordPositions, setKeywordPositions] = useState<Record<string, { bias: PositionBias; magnitude: number }>>({});
  const [dimensionWeights, setDimensionWeights] = useState({
    market: 0.3,
    industry: 0.25,
    policy: 0.25,
    tech: 0.2,
  });
  const [positionSensitivity, setPositionSensitivity] = useState(1.0);
  const [impactTimeframe, setImpactTimeframe] = useState<TimeFrame>('medium');
  const [excludedKeywords, setExcludedKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [newKeywordWeight, setNewKeywordWeight] = useState(5);
  const [newExcludedKeyword, setNewExcludedKeyword] = useState('');

  useEffect(() => {
    if (configData) {
      setKeywords(configData.keywords || {});
      setIndustries(configData.industries || []);
      setKeywordPositions(configData.keyword_positions || {});
      setDimensionWeights(configData.dimension_weights || {
        market: 0.3,
        industry: 0.25,
        policy: 0.25,
        tech: 0.2,
      });
      setPositionSensitivity(configData.position_sensitivity || 1.0);
      setImpactTimeframe(configData.impact_timeframe || 'medium');
      setExcludedKeywords(configData.excluded_keywords || []);
    }
  }, [configData]);

  const handleAddKeyword = () => {
    if (newKeyword && !keywords[newKeyword]) {
      setKeywords({ ...keywords, [newKeyword]: newKeywordWeight });
      setKeywordPositions({
        ...keywordPositions,
        [newKeyword]: { bias: 'neutral', magnitude: 50 }
      });
      setNewKeyword('');
      setNewKeywordWeight(5);
    }
  };

  const handleDeleteKeyword = (keyword: string) => {
    const newKeywords = { ...keywords };
    delete newKeywords[keyword];
    setKeywords(newKeywords);
    const newPositions = { ...keywordPositions };
    delete newPositions[keyword];
    setKeywordPositions(newPositions);
  };

  const handleAddIndustry = () => {
    if (newIndustry && !industries.includes(newIndustry)) {
      setIndustries([...industries, newIndustry]);
      setNewIndustry('');
    }
  };

  const handleDeleteIndustry = (industry: string) => {
    setIndustries(industries.filter((i) => i !== industry));
  };

  const handleAddExcluded = () => {
    if (newExcludedKeyword && !excludedKeywords.includes(newExcludedKeyword)) {
      setExcludedKeywords([...excludedKeywords, newExcludedKeyword]);
      setNewExcludedKeyword('');
    }
  };

  const handleDeleteExcluded = (keyword: string) => {
    setExcludedKeywords(excludedKeywords.filter((k) => k !== keyword));
  };

  const updateKeywordPosition = (keyword: string, field: 'bias' | 'magnitude', value: any) => {
    setKeywordPositions({
      ...keywordPositions,
      [keyword]: {
        ...keywordPositions[keyword],
        [field]: value,
      },
    });
  };

  const handleSave = () => {
    mutation.mutate({
      keywords,
      industries,
      keyword_positions: keywordPositions,
      dimension_weights: dimensionWeights,
      position_sensitivity: positionSensitivity,
      impact_timeframe: impactTimeframe,
      excluded_keywords: excludedKeywords,
    });
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <Typography>加载中...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>
        配置管理
      </Typography>

      <Paper>
        <Tabs
          value={tabValue}
          onChange={(e, v) => setTabValue(v)}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="相关性配置" />
          <Tab label="多空配置" />
          <Tab label="基础配置" />
          <Tab label="爬虫管理" />
          <Tab label="推送配置" />
        </Tabs>

        {/* 相关性配置 */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            关注行业
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              size="small"
              label="添加行业"
              value={newIndustry}
              onChange={(e) => setNewIndustry(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddIndustry()}
            />
            <Button variant="contained" onClick={handleAddIndustry}>
              添加
            </Button>
          </Box>
          <Box sx={{ mb: 3 }}>
            {industries.map((industry) => (
              <Chip
                key={industry}
                label={industry}
                onDelete={() => handleDeleteIndustry(industry)}
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            关键词配置
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              label="关键词"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            />
            <TextField
              size="small"
              label="权重"
              type="number"
              value={newKeywordWeight}
              onChange={(e) => setNewKeywordWeight(Number(e.target.value))}
              sx={{ width: 100 }}
            />
            <Button variant="contained" onClick={handleAddKeyword}>
              添加
            </Button>
          </Box>
          <Box sx={{ mb: 3 }}>
            {Object.entries(keywords).map(([keyword, weight]) => (
              <Chip
                key={keyword}
                label={`${keyword} (${weight})`}
                onDelete={() => handleDeleteKeyword(keyword)}
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            排除关键词
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              size="small"
              label="排除词"
              value={newExcludedKeyword}
              onChange={(e) => setNewExcludedKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddExcluded()}
            />
            <Button variant="contained" onClick={handleAddExcluded}>
              添加
            </Button>
          </Box>
          <Box>
            {excludedKeywords.map((keyword) => (
              <Chip
                key={keyword}
                label={keyword}
                onDelete={() => handleDeleteExcluded(keyword)}
                color="error"
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>
        </TabPanel>

        {/* 多空配置 */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            多空敏感度
          </Typography>
          <Box sx={{ mb: 3, maxWidth: 400 }}>
            <Slider
              value={positionSensitivity}
              onChange={(e, v) => setPositionSensitivity(v as number)}
              min={0.1}
              max={3.0}
              step={0.1}
              marks={[
                { value: 0.1, label: '低' },
                { value: 1.0, label: '正常' },
                { value: 3.0, label: '高' },
              ]}
              valueLabelDisplay="auto"
              valueLabelFormat={(v) => `${v.toFixed(1)}x`}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            影响维度权重
          </Typography>
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>市场影响 ({(dimensionWeights.market * 100).toFixed(0)}%)</Typography>
              <Slider
                value={dimensionWeights.market}
                onChange={(e, v) => setDimensionWeights({ ...dimensionWeights, market: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>行业影响 ({(dimensionWeights.industry * 100).toFixed(0)}%)</Typography>
              <Slider
                value={dimensionWeights.industry}
                onChange={(e, v) => setDimensionWeights({ ...dimensionWeights, industry: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>政策影响 ({(dimensionWeights.policy * 100).toFixed(0)}%)</Typography>
              <Slider
                value={dimensionWeights.policy}
                onChange={(e, v) => setDimensionWeights({ ...dimensionWeights, policy: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>技术影响 ({(dimensionWeights.tech * 100).toFixed(0)}%)</Typography>
              <Slider
                value={dimensionWeights.tech}
                onChange={(e, v) => setDimensionWeights({ ...dimensionWeights, tech: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            影响时间范围
          </Typography>
          <FormControl sx={{ minWidth: 200, mb: 3 }}>
            <InputLabel>时间范围</InputLabel>
            <Select
              value={impactTimeframe}
              label="时间范围"
              onChange={(e) => setImpactTimeframe(e.target.value as TimeFrame)}
            >
              <MenuItem value="short">短期</MenuItem>
              <MenuItem value="medium">中期</MenuItem>
              <MenuItem value="long">长期</MenuItem>
            </Select>
          </FormControl>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            关键词多空配置
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {Object.entries(keywords).map(([keyword]) => (
              <Card key={keyword} variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {keyword}
                    </Typography>
                    <Chip
                      label={`权重: ${keywords[keyword]}`}
                      size="small"
                      color="primary"
                    />
                  </Box>

                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>多空倾向</InputLabel>
                        <Select
                          value={keywordPositions[keyword]?.bias || 'neutral'}
                          label="多空倾向"
                          onChange={(e) => updateKeywordPosition(keyword, 'bias', e.target.value)}
                        >
                          <MenuItem value="bullish">
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <BullishIcon sx={{ color: '#22c55e' }} />
                              利多
                            </Box>
                          </MenuItem>
                          <MenuItem value="neutral">
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <NeutralIcon sx={{ color: '#6b7280' }} />
                              中性
                            </Box>
                          </MenuItem>
                          <MenuItem value="bearish">
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <BearishIcon sx={{ color: '#ef4444' }} />
                              利空
                            </Box>
                          </MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        影响幅度: {(keywordPositions[keyword]?.magnitude || 50).toFixed(0)}%
                      </Typography>
                      <Slider
                        value={keywordPositions[keyword]?.magnitude || 50}
                        onChange={(e, v) => updateKeywordPosition(keyword, 'magnitude', v)}
                        min={0}
                        max={100}
                        step={5}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(v) => `${v}%`}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </Box>
        </TabPanel>

        {/* 基础配置 */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            评分权重
          </Typography>
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>AI评分权重</Typography>
            <Slider
              defaultValue={configData?.ai_weight || 0.6}
              min={0}
              max={1}
              step={0.1}
              sx={{ maxWidth: 400 }}
            />
            <Typography gutterBottom sx={{ mt: 2 }}>规则评分权重</Typography>
            <Slider
              defaultValue={configData?.rule_weight || 0.4}
              min={0}
              max={1}
              step={0.1}
              sx={{ maxWidth: 400 }}
            />
            <Typography gutterBottom sx={{ mt: 2 }}>最低推送分数</Typography>
            <Slider
              defaultValue={configData?.min_score_threshold || 60}
              min={0}
              max={100}
              step={5}
              sx={{ maxWidth: 400 }}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            AI模型配置
          </Typography>
          <TextField
            fullWidth
            label="默认模型"
            defaultValue={configData?.default_llm_model || 'deepseek-chat'}
            sx={{ mb: 2, maxWidth: 400 }}
          />
          <FormControlLabel
            control={<Switch defaultChecked={configData?.enable_ai_summary} />}
            label="启用AI摘要"
          />
          <FormControlLabel
            control={<Switch defaultChecked={configData?.enable_ai_classification} />}
            label="启用AI分类"
          />
          <FormControlLabel
            control={<Switch defaultChecked={configData?.enable_ai_scoring} />}
            label="启用AI评分"
          />

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            V-API模型配置
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            选择要使用的V-API模型（支持多选）
          </Typography>
          
          {isLoadingVAPIModels ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {vapiModels.map((model: any) => (
                <Chip
                  key={model.id}
                  label={model.id}
                  color={selectedVAPIModels.includes(model.id) ? 'primary' : 'default'}
                  onClick={() => {
                    if (selectedVAPIModels.includes(model.id)) {
                      setSelectedVAPIModels(selectedVAPIModels.filter(id => id !== model.id));
                    } else {
                      setSelectedVAPIModels([...selectedVAPIModels, model.id]);
                    }
                  }}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          )}

          {selectedVAPIModels.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                已选择 {selectedVAPIModels.length} 个模型
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedVAPIModels.map((modelId) => (
                  <Chip
                    key={modelId}
                    label={modelId}
                    color="primary"
                    onDelete={() => setSelectedVAPIModels(selectedVAPIModels.filter(id => id !== modelId))}
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          )}
        </TabPanel>

        {/* 爬虫管理 */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            爬虫配置
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            管理信息源的启用状态和配置
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              信息源列表
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<TestIcon />}
              onClick={handleTestAllCrawlers}
              disabled={testingAll}
            >
              {testingAll ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  测试中...
                </Box>
              ) : (
                '批量测试'
              )}
            </Button>
          </Box>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {crawlers.map((crawler) => {
              const validityStatus = getValidityStatus(crawler);
              const IconComponent = validityStatus.icon;
              
              return (
                <Card key={crawler.id} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {crawler.name}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {crawler.source_url}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Chip
                          label={crawler.crawler_type}
                          size="small"
                          variant="outlined"
                        />
                        <Tooltip title={crawler.test_message || validityStatus.label}>
                          <Chip
                            icon={<IconComponent fontSize="small" />}
                            label={validityStatus.label}
                            size="small"
                            color={validityStatus.color as any}
                          />
                        </Tooltip>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<TestIcon />}
                          onClick={() => handleTestCrawler(crawler.id)}
                          disabled={testingCrawlerId === crawler.id}
                        >
                          {testingCrawlerId === crawler.id ? (
                            <CircularProgress size={16} />
                          ) : (
                            '测试'
                          )}
                        </Button>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={crawler.is_active}
                              onChange={(e) => handleToggleCrawler(crawler.id, e.target.checked)}
                              color="primary"
                            />
                          }
                          label={crawler.is_active ? '启用' : '禁用'}
                        />
                      </Box>
                    </Box>
                    
                    <Grid container spacing={2} sx={{ mt: 2 }}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="textSecondary">
                          抓取间隔: {crawler.interval_seconds}秒
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="textSecondary">
                          优先级: {crawler.priority}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="textSecondary">
                          抓取次数: {crawler.total_crawled}
                        </Typography>
                      </Grid>
                    </Grid>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      {crawler.last_test_at && (
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            最后测试: {new Date(crawler.last_test_at).toLocaleString()}
                          </Typography>
                        </Grid>
                      )}
                      {crawler.last_crawled_at && (
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="textSecondary">
                            最后抓取: {new Date(crawler.last_crawled_at).toLocaleString()}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                    
                    {crawler.test_message && (
                      <Box sx={{ mt: 2, p: 1, bgcolor: crawler.is_valid ? '#f0fdf4' : '#fef2f2', borderRadius: 1 }}>
                        <Typography variant="body2" color={crawler.is_valid ? 'success.main' : 'error.main'}>
                          {crawler.test_message}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </Box>
          
          {crawlers.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="textSecondary">
                暂无信息源配置
              </Typography>
            </Box>
          )}
        </TabPanel>

        {/* 推送配置 */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            飞书推送
          </Typography>
          <TextField
            fullWidth
            label="Webhook URL"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={<Switch defaultChecked={configData?.push_enabled} />}
            label="启用飞书推送"
          />

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            邮件推送
          </Typography>
          <TextField
            fullWidth
            label="收件人邮箱"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={<Switch />}
            label="启用邮件推送"
          />
        </TabPanel>

        <Box sx={{ p: 3, pt: 0 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleSave}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? '保存中...' : '保存配置'}
          </Button>
        </Box>
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
