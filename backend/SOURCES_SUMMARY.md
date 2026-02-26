# 信息源配置总结

## 优化日期
2026-02-26

## 最终配置

共配置 **9 个** 已验证的高质量信息源，包括 **7 个国内源** 和 **2 个国际源**。

### 国内新闻源（7 个）

#### 综合新闻（3 个）
1. **中国新闻网 - 国内**
   - URL: `http://www.chinanews.com.cn/rss/scroll-news.xml`
   - 类型：官方权威媒体
   - 更新频率：5 分钟

2. **中国新闻网 - 国际**
   - URL: `http://www.chinanews.com.cn/rss/world.xml`
   - 类型：官方权威媒体
   - 更新频率：5 分钟

3. **中国新闻网 - 财经**
   - URL: `http://www.chinanews.com.cn/rss/finance.xml`
   - 类型：官方权威媒体
   - 更新频率：5 分钟

#### 财经新闻（1 个）
4. **东方财富网 - 股票资讯**
   - URL: `http://rss.eastmoney.com/rss_stock.xml`
   - 类型：专业财经媒体
   - 更新频率：5 分钟
   - 特点：A 股市场资讯丰富

#### 科技新闻（3 个）
5. **36 氪 - 最新资讯**
   - URL: `http://www.36kr.com/feed`
   - 类型：科技媒体
   - 更新频率：5 分钟
   - 特点：互联网、创投圈新闻

6. **虎嗅网 - 最新文章**
   - URL: `http://www.huxiu.com/rss/0.xml`
   - 类型：商业评论媒体
   - 更新频率：5 分钟
   - 特点：深度商业分析

7. **爱范儿 - 最新文章**
   - URL: `http://www.ifanr.com/feed`
   - 类型：科技生活媒体
   - 更新频率：5 分钟
   - 特点：数码产品、科技生活

### 国际新闻源（2 个）

8. **BBC News - 头条新闻**
   - URL: `http://feeds.bbci.co.uk/news/rss.xml`
   - 类型：国际权威媒体
   - 更新频率：5 分钟
   - 语言：英语
   - 特点：全球新闻覆盖

9. **The Guardian - 头条新闻**
   - URL: `https://www.theguardian.com/world/rss`
   - 类型：国际权威媒体
   - 更新频率：5 分钟
   - 语言：英语
   - 特点：国际新闻、深度报道

---

## 已停用的源

以下源因网络环境问题或 RSS 地址失效已停用：

- Reuters 系列（5 个）- 连接问题
- CNBC 系列（2 个）- 连接问题
- Yahoo Finance - 连接问题
- TechCrunch - 连接问题
- The Verge - 连接问题
- 网易新闻系列 - RSS 失效
- 腾讯新闻系列 - RSS 失效
- 雪球系列 - RSS 失效
- 其他国内源 - RSS 失效

---

## 维护建议

### 定期检查
建议每周运行一次源有效性检查：
```bash
cd backend
python test_all_sources.py
```

### 备份配置
配置已备份至：`backend/backup_sources.json`

### 恢复配置
如需恢复配置，运行：
```bash
cd backend
python scripts/add_news_sources.py
```

### 添加新源
参考 `backend/scripts/add_news_sources.py` 的格式添加新的信息源。

---

## 测试记录

### 最新测试（2026-02-26）
- 测试源总数：20
- 可用源：9 (100% 已验证)
- 失效源：11 (已停用)

### 各源新闻数量
- 中国新闻网 - 国内：~30 条/次
- 中国新闻网 - 国际：~30 条/次
- 中国新闻网 - 财经：~30 条/次
- 东方财富网 - 股票资讯：~100 条/次
- 36 氪：~30 条/次
- 虎嗅网：~10 条/次
- 爱范儿：~20 条/次
- BBC News：~33 条/次
- The Guardian：~45 条/次

---

## 注意事项

1. **网络环境**：BBC 和 The Guardian 需要良好的国际网络环境
2. **更新频率**：所有源默认 5 分钟更新一次，可根据需要调整
3. **优先级**：东方财富网优先级为 6（较高），其他为 5
4. **语言处理**：国际源为英文内容，LLM 处理时需注意语言配置
