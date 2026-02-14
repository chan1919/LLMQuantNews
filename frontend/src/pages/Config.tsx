import { useState } from 'react'
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
  Divider,
} from '@mui/material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Config() {
  const [tabValue, setTabValue] = useState(0)
  const [keywords, setKeywords] = useState<string[]>(['AI', '量化', '区块链'])
  const [newKeyword, setNewKeyword] = useState('')

  const handleAddKeyword = () => {
    if (newKeyword && !keywords.includes(newKeyword)) {
      setKeywords([...keywords, newKeyword])
      setNewKeyword('')
    }
  }

  const handleDeleteKeyword = (keyword: string) => {
    setKeywords(keywords.filter((k) => k !== keyword))
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
          <Tab label="基础配置" />
          <Tab label="爬虫管理" />
          <Tab label="推送配置" />
          <Tab label="AI配置" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            关键词配置
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              size="small"
              label="添加关键词"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            />
            <Button variant="contained" onClick={handleAddKeyword}>
              添加
            </Button>
          </Box>
          <Box sx={{ mb: 3 }}>
            {keywords.map((keyword) => (
              <Chip
                key={keyword}
                label={keyword}
                onDelete={() => handleDeleteKeyword(keyword)}
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            评分权重
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography>AI评分权重: 60%</Typography>
            <Slider value={60} sx={{ width: 300 }} />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Typography>规则评分权重: 40%</Typography>
            <Slider value={40} sx={{ width: 300 }} />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Typography>最低推送分数: 60</Typography>
            <Slider value={60} min={0} max={100} sx={{ width: 300 }} />
          </Box>

          <Button variant="contained" color="primary" sx={{ mt: 2 }}>
            保存配置
          </Button>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            爬虫配置
          </Typography>
          <Typography color="textSecondary">
            爬虫配置功能开发中...
          </Typography>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            飞书推送
          </Typography>
          <TextField
            fullWidth
            label="Webhook URL"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={<Switch />}
            label="启用飞书推送"
          />

          <Divider sx={{ my: 2 }} />

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

          <Box sx={{ mt: 2 }}>
            <Button variant="contained" color="primary">
              保存推送配置
            </Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            AI模型配置
          </Typography>
          <TextField
            fullWidth
            label="默认模型"
            defaultValue="gpt-4o"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={<Switch defaultChecked />}
            label="启用AI摘要"
          />
          <FormControlLabel
            control={<Switch defaultChecked />}
            label="启用AI分类"
          />
          <FormControlLabel
            control={<Switch defaultChecked />}
            label="启用AI评分"
          />

          <Box sx={{ mt: 2 }}>
            <Button variant="contained" color="primary">
              保存AI配置
            </Button>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  )
}
