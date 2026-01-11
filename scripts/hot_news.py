#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量热点推送脚本 v8 - 简洁清爽版
"""

import os
import requests
import re
from datetime import datetime
from html import unescape
from concurrent.futures import ThreadPoolExecutor, as_completed

# ========== 配置 ==========
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK_URL', '')
PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '8e0bf11cb33c456aa7f77b5325a50fa0')
PUSHPLUS_URL = 'http://www.pushplus.plus/send'
API_URL = "https://newsnow.busiyi.world/api/s"

# 平台配置 (id, 名称, 图标, 品牌色, 条数)
PLATFORMS = [
    ("weibo", "微博", "📛", "#ff4d4f", 15),
    ("douyin", "抖音", "🎬", "#000000", 12),
    ("bilibili-hot-search", "B站", "📺", "#fb7299", 12),
    ("zhihu", "知乎", "🧠", "#0066ff", 12),
    ("baidu", "百度", "🔍", "#2932e1", 12),
    ("toutiao", "头条", "⚡", "#ff0000", 12),
    ("36kr-renqi", "36氪", "🚀", "#0078ff", 8),
    ("ithome", "IT之家", "💻", "#d32f2f", 8),
    ("hupu", "虎扑", "🏀", "#e31d1a", 8),
    ("wallstreetcn-hot", "华尔街见闻", "📈", "#1a73e8", 8),
]

def strip_html(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', str(text))
    return re.sub(r'\s+', ' ', unescape(text)).strip()

def format_hot(hot):
    if not hot:
        return ''
    hot = strip_html(str(hot))
    if '万' in hot or '亿' in hot:
        return hot.replace('热度', '').strip()
    try:
        num = int(re.sub(r'[^\d]', '', hot))
        if num >= 100000000:
            return f"{num/100000000:.1f}亿"
        elif num >= 10000:
            return f"{num/10000:.0f}万"
        elif num > 0:
            return f"{num:,}"
    except:
        pass
    return hot[:10] if len(hot) > 10 else hot


def fetch_platform(pid, name, icon, color, limit):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://newsnow.busiyi.world/'
    }
    try:
        resp = requests.get(f"{API_URL}?id={pid}&latest", headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get('data', data.get('items', []))[:limit]
        
        result = []
        for i, item in enumerate(items, 1):
            title = strip_html(item.get('title', ''))
            url = item.get('url', item.get('mobileUrl', ''))
            hot = format_hot(item.get('hot') or item.get('extra', {}).get('hot') or '')
            if title and url:
                result.append({'rank': i, 'title': title, 'url': url, 'hot': hot})
        
        return {'id': pid, 'name': name, 'icon': icon, 'color': color, 'items': result}
    except Exception as e:
        print(f"[{name}] 获取失败: {e}")
        return {'id': pid, 'name': name, 'icon': icon, 'color': color, 'items': []}


def fetch_all_platforms():
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_platform, *p): p[1] for p in PLATFORMS}
        for future in as_completed(futures):
            result = future.result()
            if result['items']:
                results.append(result)
    
    order = {p[0]: i for i, p in enumerate(PLATFORMS)}
    results.sort(key=lambda x: order.get(x['id'], 99))
    return results


def build_pushplus_content(platforms):
    """简洁清爽风格"""
    now = datetime.now().strftime('%m月%d日 %H:%M')
    total = sum(len(p['items']) for p in platforms)
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:-apple-system,sans-serif;background:#f8f9fa;margin:0;padding:12px;font-size:14px;color:#333}}
.header{{text-align:center;padding:16px 0;margin-bottom:12px}}
.header h1{{font-size:20px;margin:0 0 6px;color:#333}}
.header p{{font-size:12px;color:#999;margin:0}}
.card{{background:#fff;border-radius:10px;margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,0.06)}}
.card-title{{padding:12px 14px;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;font-weight:600;font-size:15px}}
.card-title .icon{{margin-right:8px;font-size:18px}}
.card-title .name{{color:#333}}
.item{{padding:10px 14px;border-bottom:1px solid #f5f5f5;display:flex;align-items:flex-start}}
.item:last-child{{border-bottom:none}}
.num{{width:22px;height:22px;border-radius:5px;text-align:center;line-height:22px;font-size:12px;font-weight:bold;margin-right:10px;flex-shrink:0}}
.num1{{background:#ff4757;color:#fff}}
.num2{{background:#ff6b81;color:#fff}}
.num3{{background:#ffa502;color:#fff}}
.num-other{{background:#f1f2f6;color:#666}}
.info{{flex:1;min-width:0}}
.title{{line-height:1.5;word-break:break-word}}
.title a{{color:#333;text-decoration:none}}
.title a.hot1{{color:#e74c3c}}
.title a.hot2{{color:#e67e22}}
.hot-val{{font-size:11px;color:#aaa;margin-top:3px}}
</style></head><body>
<div class="header"><h1>🔥 全球热点汇总 🔥</h1><p>{now} · {len(platforms)}平台 · {total}条</p></div>
'''
    
    for p in platforms:
        html += f'<div class="card"><div class="card-title"><span class="icon">{p["icon"]}</span><span class="name">{p["name"]}</span></div>'
        
        for item in p['items']:
            r = item['rank']
            if r == 1:
                num_cls, title_cls = 'num1', 'hot1'
            elif r == 2:
                num_cls, title_cls = 'num2', 'hot1'
            elif r == 3:
                num_cls, title_cls = 'num3', 'hot2'
            else:
                num_cls, title_cls = 'num-other', ''
            
            hot_html = f'<div class="hot-val">🔥 {item["hot"]}</div>' if item['hot'] else ''
            
            html += f'<div class="item"><span class="num {num_cls}">{r}</span><div class="info"><div class="title"><a href="{item["url"]}" class="{title_cls}">{item["title"]}</a></div>{hot_html}</div></div>'
        
        html += '</div>'
    
    html += '</body></html>'
    return html


def build_feishu_card(platforms):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    total = sum(len(p['items']) for p in platforms)
    
    elements = [{"tag": "markdown", "content": f"**🔥 全网热点速递**\n{now} · {len(platforms)}平台 · {total}条热点"}]
    
    for p in platforms:
        elements.append({"tag": "hr"})
        elements.append({"tag": "markdown", "content": f"**{p['icon']} {p['name']}**"})
        
        lines = []
        for item in p['items']:
            r = item['rank']
            dot = '🔴' if r <= 3 else ('🟠' if r <= 6 else '🔵')
            hot_str = f" `{item['hot']}`" if item['hot'] else ''
            lines.append(f"{dot} [{item['title']}]({item['url']}){hot_str}")
        
        elements.append({"tag": "markdown", "content": '\n'.join(lines)})
    
    return {"msg_type": "interactive", "card": {"header": {"title": {"tag": "plain_text", "content": "📊 今日热点汇总"}, "template": "red"}, "elements": elements}}


def send_to_pushplus(content):
    if not PUSHPLUS_TOKEN:
        print("❌ PushPlus Token 未配置")
        return False
    try:
        resp = requests.post(PUSHPLUS_URL, json={
            'token': PUSHPLUS_TOKEN,
            'title': f'🔥 全球热点 {datetime.now().strftime("%m-%d %H:%M")}',
            'content': content,
            'template': 'html'
        }, timeout=30)
        result = resp.json()
        if result.get('code') == 200:
            print("✅ PushPlus 推送成功")
            return True
        print(f"❌ PushPlus 推送失败: {result.get('msg')}")
        return False
    except Exception as e:
        print(f"❌ PushPlus 推送异常: {e}")
        return False


def send_to_feishu(card):
    if not FEISHU_WEBHOOK:
        print("⚠️ 飞书 Webhook 未配置，跳过")
        return False
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=card, timeout=30)
        result = resp.json()
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print("✅ 飞书推送成功")
            return True
        print(f"❌ 飞书推送失败: {result}")
        return False
    except Exception as e:
        print(f"❌ 飞书推送异常: {e}")
        return False


def main():
    print("=" * 40)
    print("🚀 热点推送 v8 - 简洁清爽版")
    print("=" * 40)
    
    print("\n📡 获取热点中...")
    platforms = fetch_all_platforms()
    
    if not platforms:
        print("❌ 未获取到数据")
        return
    
    total = sum(len(p['items']) for p in platforms)
    print(f"✅ {len(platforms)}平台 {total}条热点")
    
    print("\n📤 推送中...")
    send_to_pushplus(build_pushplus_content(platforms))
    send_to_feishu(build_feishu_card(platforms))
    
    print("\n✅ 完成")


if __name__ == '__main__':
    main()
