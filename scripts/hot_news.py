#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日热点推送脚本
抓取多个平台热榜，推送到飞书群
"""

import os
import json
import requests
from datetime import datetime

# 飞书 Webhook 地址（从环境变量获取）
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK_URL', '')

# 热榜 API（使用免费的 API）
HOT_APIS = {
    '微博热搜': 'https://api.vvhan.com/api/hotlist/wbHot',
    '知乎热榜': 'https://api.vvhan.com/api/hotlist/zhihuHot',
    '百度热搜': 'https://api.vvhan.com/api/hotlist/baiduRD',
    '抖音热榜': 'https://api.vvhan.com/api/hotlist/douyinHot',
    '今日头条': 'https://api.vvhan.com/api/hotlist/toutiao',
}


def fetch_hot_list(name: str, url: str, limit: int = 10) -> list:
    """抓取热榜数据"""
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data.get('success'):
            items = data.get('data', [])[:limit]
            return [
                {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'hot': item.get('hot', '')
                }
                for item in items
            ]
    except Exception as e:
        print(f"抓取 {name} 失败: {e}")
    
    return []


def build_feishu_card(hot_data: dict) -> dict:
    """构建飞书消息卡片"""
    
    # 当前时间
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 构建卡片元素
    elements = []
    
    for platform, items in hot_data.items():
        if not items:
            continue

        # 平台标题
        elements.append({
            "tag": "markdown",
            "content": f"**🔥 {platform}**"
        })
        
        # 热榜内容
        content_lines = []
        for i, item in enumerate(items, 1):
            title = item['title']
            url = item.get('url', '')
            
            if url:
                content_lines.append(f"{i}. [{title}]({url})")
            else:
                content_lines.append(f"{i}. {title}")
        
        elements.append({
            "tag": "markdown",
            "content": "\n".join(content_lines)
        })
        
        # 分割线
        elements.append({
            "tag": "hr"
        })
    
    # 底部时间
    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": f"更新时间：{now}"
            }
        ]
    })
    
    # 完整卡片结构
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 今日热点速览"
                },
                "template": "red"
            },
            "elements": elements
        }
    }
    
    return card


def send_to_feishu(card: dict) -> bool:
    """发送消息到飞书"""
    if not FEISHU_WEBHOOK:
        print("错误：未配置 FEISHU_WEBHOOK_URL")
        return False
    
    try:
        resp = requests.post(
            FEISHU_WEBHOOK,
            json=card,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        result = resp.json()
        
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print("✅ 推送成功！")
            return True
        else:
            print(f"❌ 推送失败：{result}")
            return False
            
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False


def main():
    print("🚀 开始抓取热点...")
    
    # 抓取各平台热榜
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
    
    # 构建消息卡片
    print("\n📝 构建消息卡片...")
    card = build_feishu_card(hot_data)
    
    # 发送到飞书
    print("\n📤 发送到飞书...")
    send_to_feishu(card)


if __name__ == '__main__':
    main()
