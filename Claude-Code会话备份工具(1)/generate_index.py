"""
Claude Code 会话索引生成器
- 扫描备份目录中的所有 .jsonl 文件
- 提取会话信息（日期、项目、主题）
- 生成 sessions.json 索引文件
- 支持定时任务运行
- 支持 AI 提取主题（需配置 API Key）
"""
import sys
import os
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# === 配置区（由 install.py 替换）===
BACKUP_DIR = Path(r"__BACKUP_DIR__")
INDEX_FILE = BACKUP_DIR / "sessions.json"

# AI 主题提取配置（可选）
# 填写 API_KEY 后将使用 AI 提取主题，留空则使用简单截取方式
AI_API_KEY = ""  # 例如: "sk-xxx"
AI_API_BASE = "https://api.openai.com/v1"  # 可改为其他兼容接口
AI_MODEL = "gpt-4o-mini"  # 推荐使用便宜快速的模型
# === 配置区结束 ===

MAX_TOPIC_LENGTH = 30


def extract_topic_with_ai(messages):
    """
    使用 AI API 提取主题摘要

    Args:
        messages: 用户消息列表

    Returns:
        str: AI 生成的主题摘要，失败时返回 None
    """
    if not AI_API_KEY or not messages:
        return None

    # 合并所有消息，清理系统标签
    cleaned_messages = []
    for msg in messages:
        cleaned = re.sub(r'<[^>]+>.*?</[^>]+>', '', msg, flags=re.DOTALL)
        cleaned = re.sub(r'<[^>]+/>', '', cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            cleaned_messages.append(cleaned)

    if not cleaned_messages:
        return None

    # 合并消息，限制总长度（避免 token 过多）
    combined = " | ".join(cleaned_messages)
    if len(combined) > 1000:
        combined = combined[:1000]

    prompt = f"请用一句话（不超过30个字）概括以下对话的主题，直接输出主题，不要加引号或其他符号：\n\n{combined}"

    try:
        request_data = {
            "model": AI_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }

        request_body = json.dumps(request_data, ensure_ascii=False).encode('utf-8')

        req = urllib.request.Request(
            f"{AI_API_BASE}/chat/completions",
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {AI_API_KEY}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

            if result.get("choices") and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                topic = content.strip()
                # 确保 AI 输出不会太长
                if len(topic) > MAX_TOPIC_LENGTH + 3:
                    topic = topic[:MAX_TOPIC_LENGTH] + "..."
                return topic

    except urllib.error.HTTPError as e:
        print(f"⚠️ AI API HTTP 错误: {e.code}")
    except urllib.error.URLError as e:
        print(f"⚠️ AI API 网络错误: {e.reason}")
    except Exception as e:
        print(f"⚠️ AI API 调用失败: {e}")

    return None


def extract_topic_simple(messages):
    """
    简单方式提取主题（取第一条消息，截取前 N 个字符）

    规则:
    1. 取第一条用户消息
    2. 去除系统标签（如 <ide_opened_file>...</ide_opened_file>）
    3. 去除首尾空白和标点
    4. 截取前 MAX_TOPIC_LENGTH 个字符
    """
    if not messages:
        return ""

    # 取第一条消息
    message = messages[0]

    # 去除系统标签
    cleaned = re.sub(r'<[^>]+>.*?</[^>]+>', '', message, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+/>', '', cleaned)

    # 去除首尾空白
    cleaned = cleaned.strip()

    # 去除首尾标点（保留中文标点）
    cleaned = re.sub(r'^[\s\-:：,，。！？、]+', '', cleaned)
    cleaned = re.sub(r'[\s\-:：,，。！？、]+$', '', cleaned)

    # 截取
    if len(cleaned) > MAX_TOPIC_LENGTH:
        cleaned = cleaned[:MAX_TOPIC_LENGTH] + "..."

    return cleaned


def extract_topic(messages):
    """
    提取主题（根据配置自动选择 AI 或简单方式）

    Args:
        messages: 用户消息列表

    Returns:
        str: 提取的主题
    """
    # 如果配置了 API Key，尝试使用 AI 提取
    if AI_API_KEY:
        ai_topic = extract_topic_with_ai(messages)
        if ai_topic:
            return ai_topic
        # AI 提取失败，回退到简单方式
        print("ℹ️ AI 提取失败，使用简单截取方式")

    # 没有 API Key 或 AI 提取失败，使用简单方式
    return extract_topic_simple(messages)


def parse_jsonl_session(file_path):
    """
    解析单个 jsonl 文件，提取会话信息

    Returns:
        dict: {"date": ..., "time": ..., "project": ..., "topic": ...}
        None: 解析失败
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            user_messages = []  # 收集所有用户消息
            timestamp = None
            cwd = None

            for line in f:
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                # 提取时间戳（从第一个有 timestamp 的条目）
                if timestamp is None and "timestamp" in entry:
                    timestamp = entry["timestamp"]

                # 提取工作目录
                if cwd is None and "cwd" in entry:
                    cwd = entry["cwd"]

                # 提取所有用户消息（type=user）
                if entry.get("type") == "user":
                    message = entry.get("message", {})
                    content = message.get("content", [])
                    if isinstance(content, list):
                        # 收集所有文本，跳过系统标签
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text = item.get("text", "")
                                # 跳过系统标签（以 < 开头的）
                                if not text.strip().startswith("<"):
                                    text_parts.append(text.strip())
                            elif isinstance(item, str):
                                if not item.strip().startswith("<"):
                                    text_parts.append(item.strip())
                        # 合并所有非系统文本
                        if text_parts:
                            user_messages.append(" ".join(text_parts))
                    elif isinstance(content, str):
                        user_messages.append(content)

            if timestamp is None:
                return None

            # 解析时间戳
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            except ValueError:
                return None

            # 提取项目名（工作目录的最后一级）
            project = ""
            if cwd:
                project = Path(cwd).name or ""

            # 提取主题（传入所有用户消息）
            topic = extract_topic(user_messages)

            return {
                "date": date_str,
                "time": time_str,
                "project": project,
                "topic": topic
            }

    except Exception as e:
        print(f"⚠️ 解析失败 {file_path.name}: {e}")
        return None


def generate_index():
    """
    扫描备份目录，生成 sessions.json 索引
    """
    if not BACKUP_DIR.exists():
        print(f"❌ 备份目录不存在: {BACKUP_DIR}")
        return

    sessions = []

    try:
        jsonl_files = list(BACKUP_DIR.rglob("*.jsonl"))
    except Exception as e:
        print(f"❌ 扫描备份目录失败: {e}")
        return

    # 排除索引文件本身
    jsonl_files = [f for f in jsonl_files if f.name != "sessions.json"]

    print(f"📂 发现 {len(jsonl_files)} 个会话文件")

    for jsonl_path in jsonl_files:
        info = parse_jsonl_session(jsonl_path)
        if info:
            sessions.append({
                "file": jsonl_path.name,
                **info
            })

    # 按日期时间排序（最新的在前）
    sessions.sort(key=lambda x: (x["date"], x["time"]), reverse=True)

    # 构建索引
    index = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_sessions": len(sessions),
        "sessions": sessions
    }

    # 原子性写入
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = INDEX_FILE.with_suffix('.json.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        temp_file.replace(INDEX_FILE)
        print(f"✅ 索引已生成: {INDEX_FILE}")
        print(f"   共 {len(sessions)} 个会话")
    except Exception as e:
        print(f"❌ 写入索引失败: {e}")


if __name__ == '__main__':
    generate_index()
