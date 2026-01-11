# 🔥 每日热点推送

一个简单美观的热点推送系统，使用 GitHub Actions 定时抓取热榜并推送到飞书群。

## 特点

- ✅ 零成本运行（GitHub Actions 免费）
- ✅ 美观的飞书消息卡片
- ✅ 支持多个热榜平台
- ✅ 每天定时推送
- ✅ 代码简洁可控

## 快速开始

### 1. Fork 或创建仓库

在 GitHub 上创建一个新仓库，将以下文件上传。

### 2. 配置飞书 Webhook

在仓库的 Settings → Secrets and variables → Actions 中添加：

- `FEISHU_WEBHOOK_URL`: 你的飞书机器人 Webhook 地址

### 3. 启用 Actions

进入 Actions 标签页，启用工作流即可。

## 文件结构

```
.github/
  workflows/
    daily-hot.yml    # GitHub Actions 工作流
scripts/
  hot_news.py        # 热点抓取脚本
```

## 推送效果预览

飞书群会收到美观的消息卡片，包含：
- 📊 热榜标题
- 🔗 可点击的链接
- ⏰ 更新时间
