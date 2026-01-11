#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日热点推送脚本
使用 imsyy/DailyHotApi 抓取热榜，推送到飞书群
API 部署在 Vercel，全球可访问
"""

import os
import requests
from datetime import datetime

FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK_URL', '')

# 使用 DailyHotApi (https://github.com/imsyy/DailyHotApi)
# 这个 API 部署在 Vercel 上，全球可访问
HOT_APIS = {
    '微博热搜': 'https://dailyhot.hkg1.zeabur.app/weibo',
    '知乎热榜': 'https://dailyhot.hkg1.zeabur.app/zhihu',
    '百度热搜': 'https://dailyhot.hkg1.zeabur.app/baidu',
    '抖音热榜': 'https://dailyhot.hkg1.zeabur.app/douyin',
    '今日头条': 'https://dailyhot.hkg1.zeabur.app/toutiao',
}

def fetch_hot_list(name, url, limit=10):
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        data = resp.json()
        if data.get('code') == 200:
            items = data.get('data', [])[:limit]
            return [{'title': item.get('title', ''), 'url': item.get('url', item.get('mobileUrl', ''))} for item in items]
    except Exception as e:
        print(f"抓取 {name} 失败: {e}")
    return []

def build_feishu_card(hot_data):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    elements = []
    for platform, items in hot_data.items():
        if not items:
            continue
        elements.append({"tag": "markdown", "content": f"**🔥 {platform}**"})
        lines = [f"{i}. [{item['title']}]({item['url']})" if item.get('url') else f"{i}. {item['title']}" for i, item in enumerate(items, 1)]
        elements.append({"tag": "markdown", "content": "\n".join(lines)})
        elements.append({"tag": "hr"})
    elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": f"更新时间：{now}"}]})
    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "📊 今日热点速览"}, "template": "red"},
            "elements": elements
        }
    }

def send_to_feishu(card):
    if not FEISHU_WEBHOOK:
        print("错误：未配置 FEISHU_WEBHOOK_URL")
        return False
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=card, headers={'Content-Type': 'application/json'}, timeout=10)
        result = resp.json()
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print("✅ 推送成功！")
            return True
        print(f"❌ 推送失败：{result}")
        return False
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False

def main():
    print("🚀 开始抓取热点...")
    hot_data = {}
    for name, url in HOT_APIS.items():
        print(f"  抓取 {name}...")
        items = fetch_hot_list(name, url, limit=10)
        if items:
            hot_data[name] = items
            print(f"    获取 {len(items)} 条")
        else:
            print(f"    获取失败")
    if not hot_data:
        print("❌ 未获取到任何热点数据")
        return
    print("\n📝 构建消息卡片...")
    card = build_feishu_card(hot_data)
    print("\n📤 发送到飞书...")
    send_to_feishu(card)

if __name__ == '__main__':
    main()
