import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List

from .base import BasePusher, PushResult
from app.config import settings

class EmailPusher(BasePusher):
    """邮件推送"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_host = config.get('smtp_host') or settings.SMTP_HOST
        self.smtp_port = config.get('smtp_port') or settings.SMTP_PORT
        self.smtp_user = config.get('smtp_user') or settings.SMTP_USER
        self.smtp_pass = config.get('smtp_pass') or settings.SMTP_PASS
        self.use_tls = config.get('use_tls', True)
        self.recipients = config.get('recipients', [])
    
    async def push(self, news_item: Dict[str, Any]) -> PushResult:
        """推送新闻邮件"""
        try:
            if not self.recipients:
                return PushResult(
                    success=False,
                    channel='email',
                    error_message='未配置收件人'
                )
            
            # 构建邮件
            msg = self._build_email(news_item)
            
            # 发送邮件
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_pass,
                start_tls=self.use_tls
            )
            
            return PushResult(
                success=True,
                channel='email',
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return PushResult(
                success=False,
                channel='email',
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def _build_email(self, news_item: Dict[str, Any]) -> MIMEMultipart:
        """构建邮件内容"""
        score = news_item.get('final_score', 0)
        title = news_item.get('title', '无标题')
        summary = news_item.get('summary', '')
        content = news_item.get('content', '')[:2000]
        source = news_item.get('source', '未知来源')
        url = news_item.get('url', '')
        categories = ', '.join(news_item.get('categories', []))
        keywords = ', '.join(news_item.get('keywords', []))
        
        # 优先级标签
        if score >= 85:
            priority_label = "🔴 重要"
        elif score >= 70:
            priority_label = "🟡 关注"
        else:
            priority_label = "🟢 一般"
        
        # 构建HTML内容
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .score {{ font-size: 48px; font-weight: bold; }}
                .title {{ font-size: 24px; margin: 10px 0; }}
                .meta {{ color: #666; margin: 10px 0; }}
                .content {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
                .tags {{ margin: 10px 0; }}
                .tag {{ display: inline-block; background: #e0e0e0; padding: 4px 12px; border-radius: 12px; margin-right: 8px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="score">{score}%</div>
                <div class="title">{priority_label} {title}</div>
            </div>
            
            <div class="meta">
                <strong>📎 来源:</strong> {source}<br>
                <strong>🏷️ 分类:</strong> {categories}<br>
                <strong>🔑 关键词:</strong> {keywords}
            </div>
            
            <div class="content">
                <h3>摘要</h3>
                <p>{summary}</p>
                
                <h3>正文预览</h3>
                <p>{content}...</p>
            </div>
            
            <a href="{url}" class="button">阅读完整文章</a>
            
            <hr style="margin-top: 40px;">
            <p style="color: #999; font-size: 12px;">
                此邮件由 LLMQuant News 自动发送<br>
                发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{priority_label}] {title[:60]}"
        msg['From'] = self.smtp_user
        msg['To'] = ', '.join(self.recipients)
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    async def test_connection(self) -> bool:
        """测试SMTP连接"""
        try:
            await aiosmtplib.connect(
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_pass,
                start_tls=self.use_tls
            )
            return True
        except:
            return False
