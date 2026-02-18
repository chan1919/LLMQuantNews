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
  Card,
  CardContent,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  Divider,
  FormControl,
  RadioGroup,
  Radio,
  FormLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
} from '@mui/material';
import {
  Psychology as AIIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  Block as BlockIcon,
  ThumbUp as LikeIcon,
  ThumbDown as DislikeIcon,
  AutoFixHigh as MagicIcon,
} from '@mui/icons-material';
import axios from 'axios';
import type { UserConfig, TimeFrame, AIConfigAnalysis } from '../types';

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

// API函数
const fetchConfig = async (): Promise<UserConfig> => {
  const { data } = await axios.get(`${API_URL}/config/user`);
  return data;
};

const saveConfig = async (config: Partial<UserConfig>): Promise<UserConfig> => {
  const { data } = await axios.put(`${API_URL}/config/user`, config);
  return data;
};

const analyzeDescription = async (description: string, previewOnly: boolean = true): Promise<AIConfigAnalysis> => {
  const { data } = await axios.post(`${API_URL}/config/analyze-description`, {
    description,
    preview_only: previewOnly
  });
  return data.config;
};

const applyAIConfig = async (confirmed: boolean = true) => {
  const { data } = await axios.post(`${API_URL}/config/apply-ai-config`, { confirmed });
  return data;
};

const rejectAIConfig = async () => {
  const { data } = await axios.post(`${API_URL}/config/reject-ai-config`);
  return data;
};

const getPendingAIConfig = async () => {
  const { data } = await axios.get(`${API_URL}/config/pending-ai-config`);
  return data;
};

const getPreferredSources = async () => {
  const { data } = await axios.get(`${API_URL}/config/preferred-sources`);
  return data;
};

const updateSourceWeight = async (sourceName: string, weight: number) => {
  const { data } = await axios.post(`${API_URL}/config/preferred-sources/update-weight`, {
    source_name: sourceName,
    weight
  });
  return data;
};

const blockSource = async (sourceName: string) => {
  const { data } = await axios.post(`${API_URL}/config/block-source`, { source_name: sourceName });
  return data;
};

const unblockSource = async (sourceName: string) => {
  const { data } = await axios.post(`${API_URL}/config/unblock-source`, { source_name: sourceName });
  return data;
};

const fetchCrawlers = async (): Promise<any[]> => {
  const { data } = await axios.get(`${API_URL}/config/crawlers`);
  return data;
};

type PositionBias = 'bullish' | 'bearish' | 'neutral';

export default function Config() {
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'info' });

  // 查询
  const { data: configData, isLoading } = useQuery({
    queryKey: ['userConfig'],
    queryFn: fetchConfig,
  });

  const { data: crawlers = [] } = useQuery({
    queryKey: ['crawlers'],
    queryFn: fetchCrawlers,
  });

  const { data: pendingConfig } = useQuery({
    queryKey: ['pendingAIConfig'],
    queryFn: getPendingAIConfig,
  });

  const { data: preferredSourcesData } = useQuery({
    queryKey: ['preferredSources'],
    queryFn: getPreferredSources,
  });

  // 本地状态
  const [configMode, setConfigMode] = useState<'keywords' | 'description' | 'hybrid'>('keywords');
  const [userDescription, setUserDescription] = useState('');
  const [aiConfigPreview, setAiConfigPreview] = useState<AIConfigAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  
  // 原有的状态
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

  // Mutations
  const analyzeMutation = useMutation({
    mutationFn: ({ description, preview }: { description: string; preview: boolean }) => 
      analyzeDescription(description, preview),
    onMutate: () => {
      setIsAnalyzing(true);
    },
    onSuccess: (data) => {
      setAiConfigPreview(data);
      setIsAnalyzing(false);
      setSnackbar({ open: true, message: 'AI分析完成', severity: 'success' });
    },
    onError: () => {
      setIsAnalyzing(false);
      setSnackbar({ open: true, message: 'AI分析失败', severity: 'error' });
    },
  });

  const applyConfigMutation = useMutation({
    mutationFn: applyAIConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userConfig'] });
      queryClient.invalidateQueries({ queryKey: ['pendingAIConfig'] });
      setShowConfirmDialog(false);
      setAiConfigPreview(null);
      setSnackbar({ open: true, message: 'AI配置已应用', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: '应用配置失败', severity: 'error' });
    },
  });

  const rejectConfigMutation = useMutation({
    mutationFn: rejectAIConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingAIConfig'] });
      setAiConfigPreview(null);
      setSnackbar({ open: true, message: '已拒绝AI配置', severity: 'info' });
    },
  });

  const saveMutation = useMutation({
    mutationFn: saveConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userConfig'] });
      setSnackbar({ open: true, message: '保存成功', severity: 'success' });
    },
    onError: () => {
      setSnackbar({ open: true, message: '保存失败', severity: 'error' });
    },
  });

  // 初始化数据
  useEffect(() => {
    if (configData) {
      setKeywords(configData.keywords || {});
      setIndustries(configData.industries || []);
      setKeywordPositions(configData.keyword_positions || {});
      setDimensionWeights(configData.dimension_weights || { market: 0.3, industry: 0.25, policy: 0.25, tech: 0.2 });
      setPositionSensitivity(configData.position_sensitivity || 1.0);
      setImpactTimeframe(configData.impact_timeframe || 'medium');
      setExcludedKeywords(configData.excluded_keywords || []);
      setUserDescription(configData.user_description || '');
      setConfigMode(configData.analysis_mode || 'keywords');
    }
  }, [configData]);

  // 处理AI分析
  const handleAnalyzeDescription = () => {
    if (!userDescription.trim()) {
      setSnackbar({ open: true, message: '请输入描述内容', severity: 'error' });
      return;
    }
    analyzeMutation.mutate({ description: userDescription, preview: false });
  };

  // 处理保存
  const handleSave = () => {
    saveMutation.mutate({
      keywords,
      industries,
      keyword_positions: keywordPositions,
      dimension_weights: dimensionWeights,
      position_sensitivity: positionSensitivity,
      impact_timeframe: impactTimeframe,
      excluded_keywords: excludedKeywords,
      analysis_mode: configMode,
      user_description: userDescription,
    });
  };

  // 处理关键词
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

  // 处理行业
  const handleAddIndustry = () => {
    if (newIndustry && !industries.includes(newIndustry)) {
      setIndustries([...industries, newIndustry]);
      setNewIndustry('');
    }
  };

  const handleDeleteIndustry = (industry: string) => {
    setIndustries(industries.filter((i) => i !== industry));
  };

  // 处理排除词
  const handleAddExcluded = () => {
    if (newExcludedKeyword && !excludedKeywords.includes(newExcludedKeyword)) {
      setExcludedKeywords([...excludedKeywords, newExcludedKeyword]);
      setNewExcludedKeyword('');
    }
  };

  const handleDeleteExcluded = (keyword: string) => {
    setExcludedKeywords(excludedKeywords.filter((k) => k !== keyword));
  };

  // 渲染配置模式选择
  const renderConfigModeSelector = () => (
    <Box sx={{ mb: 3 }}>
      <FormControl component="fieldset">
        <FormLabel component="legend">配置模式</FormLabel>
        <RadioGroup
          row
          value={configMode}
          onChange={(e) => setConfigMode(e.target.value as 'keywords' | 'description')}
        >
          <FormControlLabel 
            value="keywords" 
            control={<Radio />} 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SettingsIcon fontSize="small" />
                关键词配置
              </Box>
            }
          />
          <FormControlLabel 
            value="description" 
            control={<Radio />} 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AIIcon fontSize="small" />
                AI智能配置
              </Box>
            }
          />
        </RadioGroup>
      </FormControl>
    </Box>
  );

  // 渲染AI配置预览
  const renderAIConfigPreview = () => {
    if (!aiConfigPreview) return null;

    return (
      <Card variant="outlined" sx={{ mt: 3, bgcolor: '#f8fafc' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">
              AI生成的配置预览
            </Typography>
          </Box>

          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="bold">关键词配置</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(aiConfigPreview.keywords || {}).map(([keyword, weight]) => (
                  <Chip
                    key={keyword}
                    label={`${keyword} (${weight})`}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="bold">关注行业</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {(aiConfigPreview.industries || []).map((industry) => (
                  <Chip key={industry} label={industry} color="secondary" />
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="bold">推荐信息源</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(aiConfigPreview.recommended_sources || {}).map(([source, weight]) => (
                  <Chip
                    key={source}
                    label={`${source} (${weight})`}
                    variant="outlined"
                  />
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="bold">排除关键词</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {(aiConfigPreview.excluded_keywords || []).map((keyword) => (
                  <Chip key={keyword} label={keyword} color="error" />
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>

          <Box sx={{ mt: 2, p: 2, bgcolor: '#e0f2fe', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              <strong>分析理由：</strong>{aiConfigPreview.analysis_reasoning}
            </Typography>
          </Box>

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<LikeIcon />}
              onClick={() => setShowConfirmDialog(true)}
            >
              应用此配置
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DislikeIcon />}
              onClick={() => rejectConfigMutation.mutate()}
            >
              拒绝
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  // 渲染智能偏好配置
  const renderSmartConfig = () => (
    <Box>
      {renderConfigModeSelector()}

      {configMode === 'description' ? (
        <Box>
          <Typography variant="h6" gutterBottom>
            用自然语言描述您的偏好
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            请描述您的投资风格、关注的行业和话题、对哪些信息敏感、希望看到什么样的新闻等。
            AI会根据您的描述自动生成个性化的配置。
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={6}
            label="描述您的偏好"
            placeholder="例如：我是A股价值投资者，主要关注科技和新能源板块，对政策变化非常敏感。我不喜欢短期炒作的消息，更关注公司的基本面和长期发展趋势..."
            value={userDescription}
            onChange={(e) => setUserDescription(e.target.value)}
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            color="primary"
            startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <AIIcon />}
            onClick={handleAnalyzeDescription}
            disabled={isAnalyzing || !userDescription.trim()}
            size="large"
          >
            {isAnalyzing ? 'AI分析中...' : '让AI分析我的偏好'}
          </Button>

          {isAnalyzing && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                AI正在分析您的描述，生成个性化配置...
              </Typography>
            </Box>
          )}

          {renderAIConfigPreview()}

          {pendingConfig?.has_pending && (
            <Alert severity="info" sx={{ mt: 3 }}>
              您有未处理的AI配置建议，请在上方查看并确认
            </Alert>
          )}
        </Box>
      ) : (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            您正在使用关键词配置模式。如需使用AI智能配置，请在上方切换配置模式。
          </Alert>
          
          <Typography variant="body2" color="text.secondary">
            请在"相关性配置"和"多空配置"标签页中手动设置关键词、行业等配置。
          </Typography>
        </Box>
      )}
    </Box>
  );

  // 渲染信息源偏好管理
  const renderSourcePreferences = () => {
    const allSources = crawlers.map(c => c.name);
    const preferred = preferredSourcesData?.preferred || {};
    const blocked = preferredSourcesData?.blocked || [];
    const aiRecommended = preferredSourcesData?.ai_recommended || [];

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          信息源偏好管理
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          调整各信息源的权重以影响新闻排序，或屏蔽不想看到的信息源。
        </Typography>

        {/* AI推荐信息源 */}
        {aiRecommended.length > 0 && (
          <>
            <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
              <AIIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
              AI推荐的信息源
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {aiRecommended.map((source: string) => (
                <Chip
                  key={source}
                  label={source}
                  color="primary"
                  variant="outlined"
                  icon={<MagicIcon />}
                />
              ))}
            </Box>
            <Divider sx={{ my: 2 }} />
          </>
        )}

        {/* 信息源列表 */}
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
          所有信息源
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {allSources.map((sourceName) => {
            const isBlocked = blocked.includes(sourceName);
            const weight = preferred[sourceName] || 1.0;
            const isAIRecommended = aiRecommended.includes(sourceName);

            return (
              <Card 
                key={sourceName} 
                variant="outlined"
                sx={{ 
                  opacity: isBlocked ? 0.5 : 1,
                  bgcolor: isAIRecommended ? '#f0f9ff' : 'inherit'
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" fontWeight={isAIRecommended ? 'bold' : 'normal'}>
                        {sourceName}
                      </Typography>
                      {isAIRecommended && (
                        <Tooltip title="AI推荐">
                          <MagicIcon fontSize="small" color="primary" />
                        </Tooltip>
                      )}
                      {isBlocked && (
                        <Chip label="已屏蔽" size="small" color="error" />
                      )}
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {!isBlocked && (
                        <>
                          <Typography variant="body2" color="text.secondary">
                            权重: {weight.toFixed(1)}
                          </Typography>
                          <Slider
                            value={weight}
                            onChange={(_, v) => {
                              updateSourceWeight(sourceName, v as number);
                            }}
                            min={0}
                            max={2}
                            step={0.1}
                            sx={{ width: 120 }}
                            disabled={isBlocked}
                          />
                        </>
                      )}
                      
                      <Tooltip title={isBlocked ? "取消屏蔽" : "屏蔽此源"}>
                        <IconButton
                          color={isBlocked ? "success" : "error"}
                          onClick={() => {
                            if (isBlocked) {
                              unblockSource(sourceName);
                            } else {
                              blockSource(sourceName);
                            }
                            queryClient.invalidateQueries({ queryKey: ['preferredSources'] });
                          }}
                        >
                           {isBlocked ? <BlockIcon color="success" /> : <BlockIcon />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            );
          })}
        </Box>

        {allSources.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              暂无信息源配置
            </Typography>
          </Box>
        )}
      </Box>
    );
  };

  // 确认对话框
  const renderConfirmDialog = () => (
    <Dialog open={showConfirmDialog} onClose={() => setShowConfirmDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AIIcon color="primary" />
          确认应用AI配置
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          您确定要应用AI生成的配置吗？这将更新您的关键词、行业、信息源偏好等设置。
        </Typography>
        <Alert severity="info">
          应用后，系统将根据新的配置为您筛选和展示新闻。您可以随时在配置页面修改这些设置。
        </Alert>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowConfirmDialog(false)}>
          取消
        </Button>
        <Button 
          variant="contained" 
          color="primary"
          onClick={() => applyConfigMutation.mutate(true)}
          disabled={applyConfigMutation.isPending}
        >
          {applyConfigMutation.isPending ? '应用中...' : '确认应用'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
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
          onChange={(_, v) => setTabValue(v)}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AIIcon />
                智能偏好
                {pendingConfig?.has_pending && (
                  <Badge variant="dot" color="error" />
                )}
              </Box>
            } 
          />
          <Tab label="相关性配置" />
          <Tab label="多空配置" />
          <Tab label="信息源管理" />
          <Tab label="基础配置" />
          <Tab label="推送配置" />
        </Tabs>

        {/* 智能偏好 */}
        <TabPanel value={tabValue} index={0}>
          {renderSmartConfig()}
        </TabPanel>

        {/* 相关性配置 */}
        <TabPanel value={tabValue} index={1}>
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
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            多空敏感度
          </Typography>
          <Box sx={{ mb: 3, maxWidth: 400 }}>
            <Slider
              value={positionSensitivity}
              onChange={(_, v) => setPositionSensitivity(v as number)}
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
                onChange={(_, v) => setDimensionWeights({ ...dimensionWeights, market: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>行业影响 ({(dimensionWeights.industry * 100).toFixed(0)}%)</Typography>
              <Slider
                value={dimensionWeights.industry}
                onChange={(_, v) => setDimensionWeights({ ...dimensionWeights, industry: v as number })}
                min={0}
                max={1}
                step={0.05}
              />
            </Grid>
          </Grid>
        </TabPanel>

        {/* 信息源管理 */}
        <TabPanel value={tabValue} index={3}>
          {renderSourcePreferences()}
        </TabPanel>

        {/* 基础配置 */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            基础设置
          </Typography>
          <TextField
            fullWidth
            label="最低推送分数"
            type="number"
            defaultValue={configData?.min_score_threshold || 60}
            sx={{ mb: 2, maxWidth: 400 }}
          />
          <FormControlLabel
            control={<Switch defaultChecked={configData?.enable_ai_summary} />}
            label="启用AI摘要"
          />
        </TabPanel>

        {/* 推送配置 */}
        <TabPanel value={tabValue} index={5}>
          <Typography variant="h6" gutterBottom>
            推送设置
          </Typography>
          <FormControlLabel
            control={<Switch defaultChecked={configData?.push_enabled} />}
            label="启用推送"
          />
        </TabPanel>

        <Box sx={{ p: 3, pt: 0 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleSave}
            disabled={saveMutation.isPending}
          >
            {saveMutation.isPending ? '保存中...' : '保存配置'}
          </Button>
        </Box>
      </Paper>

      {renderConfirmDialog()}

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
