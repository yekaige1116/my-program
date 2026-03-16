# 会话索引生成器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Claude Code 会话备份工具添加索引生成功能，生成可搜索的 JSON 索引文件。

**Architecture:** 两步式架构 - 第一步保持原有的快速同步，第二步通过定时任务扫描备份目录并生成 JSON 索引。索引包含日期、时间、项目名和从用户首条消息提取的主题。

**Tech Stack:** Python 3, JSON, launchd (macOS) / cron (Linux)

---

## Task 1: 创建索引生成器核心模块

**Files:**
- Create: `generate_index.py`

**Step 1: 创建脚本骨架和配置区**

```python
"""
Claude Code 会话索引生成器
- 扫描备份目录中的所有 .jsonl 文件
- 提取会话信息（日期、项目、主题）
- 生成 sessions.json 索引文件
- 支持定时任务运行
"""
import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# === 配置区（由 install.py 替换）===
BACKUP_DIR = Path(r"__BACKUP_DIR__")
INDEX_FILE = BACKUP_DIR / "sessions.json"
# === 配置区结束 ===

MAX_TOPIC_LENGTH = 30
```

**Step 2: 实现 jsonl 解析函数**

```python
def parse_jsonl_session(file_path):
    """
    解析单个 jsonl 文件，提取会话信息

    Returns:
        dict: {"date": ..., "time": ..., "project": ..., "topic": ...}
        None: 解析失败
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_user_message = None
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

                # 提取第一条用户消息（type=user 且 parentUuid 为 None 或不存在）
                if (first_user_message is None and
                    entry.get("type") == "user" and
                    entry.get("parentUuid") is None):
                    message = entry.get("message", {})
                    content = message.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                first_user_message = item.get("text", "")
                                break
                            elif isinstance(item, str):
                                first_user_message = item
                                break
                    elif isinstance(content, str):
                        first_user_message = content

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

            # 提取主题
            topic = extract_topic(first_user_message)

            return {
                "date": date_str,
                "time": time_str,
                "project": project,
                "topic": topic
            }

    except Exception as e:
        print(f"⚠️ 解析失败 {file_path.name}: {e}")
        return None


def extract_topic(message):
    """
    从用户消息中提取主题

    规则:
    1. 去除系统标签（如 <ide_opened_file>...</ide_opened_file>）
    2. 去除首尾空白和标点
    3. 截取前 MAX_TOPIC_LENGTH 个字符
    """
    if not message:
        return ""

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
```

**Step 3: 实现主函数和索引生成**

```python
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
```

**Step 4: 本地测试**

运行: `python generate_index.py`
预期: 在备份目录生成 `sessions.json` 文件

---

## Task 2: 更新安装脚本

**Files:**
- Modify: `install.py`

**Step 1: 添加定时任务安装函数**

在 `install.py` 中添加以下函数（在 Step 4 之前）:

```python
# ==================== Step 4.5: 部署索引生成器并配置定时任务 ====================

def setup_scheduled_indexer(backup_dir, hooks_dir):
    """
    部署索引生成器脚本并配置定时任务
    """
    # 读取模板脚本，替换路径
    script_dir = Path(__file__).parent
    template_path = script_dir / "generate_index.py"

    if not template_path.exists():
        print(f"⚠️ 未找到索引生成器模板: {template_path}")
        print("   将跳过定时任务配置")
        return False

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # 替换路径
        backup_dir_escaped = str(backup_dir).replace("\\", "\\\\")
        script_content = script_content.replace("__BACKUP_DIR__", backup_dir_escaped)

        deploy_path = hooks_dir / "generate_index.py"
        with open(deploy_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"✓ 索引生成器已部署到: {deploy_path}")
    except Exception as e:
        print(f"⚠️ 部署索引生成器失败: {e}")
        return False

    # 配置定时任务
    system = sys.platform

    if system == "darwin":
        # macOS: 使用 launchd
        return setup_launchd(hooks_dir, backup_dir)
    elif system.startswith("linux"):
        # Linux: 使用 cron
        return setup_cron(hooks_dir)
    else:
        print(f"⚠️ 不支持的系统: {system}")
        print("   请手动配置定时任务")
        return False


def setup_launchd(hooks_dir, backup_dir):
    """
    macOS: 配置 launchd 定时任务
    """
    plist_name = "com.claude.session-index"
    plist_path = Path.home() / "Library" / "LaunchAgents" / f"{plist_name}.plist"

    python_path = sys.executable
    script_path = hooks_dir / "generate_index.py"

    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/claude-session-index.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/claude-session-index.log</string>
</dict>
</plist>
'''

    try:
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        with open(plist_path, 'w', encoding='utf-8') as f:
            f.write(plist_content)

        # 加载 plist
        os.system(f"launchctl unload {plist_path} 2>/dev/null")
        os.system(f"launchctl load {plist_path}")

        print(f"✓ 定时任务已配置 (launchd)")
        print(f"  每天凌晨 2:00 自动生成索引")
        print(f"  日志: /tmp/claude-session-index.log")
        return True
    except Exception as e:
        print(f"⚠️ 配置 launchd 失败: {e}")
        return False


def setup_cron(hooks_dir):
    """
    Linux: 配置 cron 定时任务
    """
    script_path = hooks_dir / "generate_index.py"
    cron_entry = f"0 2 * * * {sys.executable} {script_path} # claude-session-index"

    try:
        # 获取当前 crontab
        result = os.popen("crontab -l 2>/dev/null").read()

        # 检查是否已存在
        if "claude-session-index" in result:
            print("✓ 定时任务已存在 (cron)")
            return True

        # 添加新条目
        new_cron = result.rstrip() + "\n" + cron_entry + "\n"

        # 写入
        process = os.popen("crontab -", "w")
        process.write(new_cron)
        process.close()

        print(f"✓ 定时任务已配置 (cron)")
        print(f"  每天凌晨 2:00 自动生成索引")
        return True
    except Exception as e:
        print(f"⚠️ 配置 cron 失败: {e}")
        return False
```

**Step 2: 在主流程中调用定时任务配置**

在 `install.py` 的主流程中，在 Step 5（首次全量同步）之前添加:

```python
# ==================== Step 4.5: 部署索引生成器并配置定时任务 ====================

print()
print("正在配置索引生成器...")
setup_scheduled_indexer(backup_dir, hooks_dir)
```

**Step 3: 测试安装脚本**

运行: `python install.py`
预期: 安装成功，显示定时任务已配置

---

## Task 3: 更新 README 文档

**Files:**
- Modify: `README.txt`

**Step 1: 添加索引功能说明**

在 `README.txt` 的"备份了什么？"部分后添加:

```
自动生成的索引
─────────────────────

除了原始会话文件，工具还会自动生成一个索引文件 sessions.json，
方便你快速搜索历史对话。

索引格式示例：
{
  "sessions": [
    {
      "date": "2026-03-04",
      "time": "13:50",
      "project": "java",
      "topic": "检测java环境是否已成功安装"
    }
  ]
}

每天凌晨 2:00 自动更新索引。

想搜索历史记录？
─────────────────────

方式一：直接问 Claude
  "帮我在 D:\我的备份目录\sessions.json 里搜索关于java的对话"

方式二：直接打开 sessions.json 搜索关键词
```

---

## Task 4: 创建卸载脚本

**Files:**
- Create: `uninstall.py`

**Step 1: 创建卸载脚本**

```python
"""
Claude Code 会话备份工具 - 卸载脚本
运行方式：python uninstall.py
"""
import sys
import os
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print()
print("=" * 50)
print("  Claude Code 会话备份工具 - 卸载程序")
print("=" * 50)
print()

home = Path.home()
claude_dir = home / ".claude"
hooks_dir = claude_dir / "hooks"
settings_path = claude_dir / "settings.json"

# 确认卸载
print("此操作将：")
print("  · 从 settings.json 中移除备份相关的 hooks")
print("  · 删除 ~/.claude/hooks/sync_raw_sessions.py")
print("  · 删除 ~/.claude/hooks/generate_index.py")
print("  · 移除定时任务")
print("  · 保留备份目录和已备份的文件")
print()

confirm = input("确认卸载？(y/N): ").strip().lower()
if confirm != 'y':
    print("已取消")
    input("按回车退出...")
    sys.exit(0)

# 1. 从 settings.json 中移除 hooks
try:
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        hooks = settings.get("hooks", {})

        # 移除包含 sync_raw_sessions 的 hooks
        for hook_name in ["Stop", "SessionEnd"]:
            if hook_name in hooks:
                hooks[hook_name] = [
                    g for g in hooks[hook_name]
                    if not any(
                        "sync_raw_sessions" in str(h.get("command", ""))
                        for h in (g.get("hooks", []) if isinstance(g, dict) else [])
                    )
                ]

        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

        print("✓ 已从 settings.json 移除 hooks")
except Exception as e:
    print(f"⚠️ 移除 hooks 失败: {e}")

# 2. 删除脚本文件
for script_name in ["sync_raw_sessions.py", "generate_index.py"]:
    script_path = hooks_dir / script_name
    if script_path.exists():
        try:
            script_path.unlink()
            print(f"✓ 已删除 {script_name}")
        except Exception as e:
            print(f"⚠️ 删除 {script_name} 失败: {e}")

# 3. 移除定时任务
system = sys.platform
if system == "darwin":
    plist_name = "com.claude.session-index"
    plist_path = Path.home() / "Library" / "LaunchAgents" / f"{plist_name}.plist"
    if plist_path.exists():
        try:
            os.system(f"launchctl unload {plist_path} 2>/dev/null")
            plist_path.unlink()
            print("✓ 已移除定时任务 (launchd)")
        except Exception as e:
            print(f"⚠️ 移除定时任务失败: {e}")
elif system.startswith("linux"):
    try:
        result = os.popen("crontab -l 2>/dev/null").read()
        new_cron = "\n".join(
            line for line in result.split("\n")
            if "claude-session-index" not in line
        )
        os.popen("crontab -", "w").write(new_cron)
        print("✓ 已移除定时任务 (cron)")
    except Exception as e:
        print(f"⚠️ 移除定时任务失败: {e}")

print()
print("=" * 50)
print("  ✅ 卸载完成")
print("  备份目录和已备份的文件已保留")
print("=" * 50)
print()

input("按回车退出...")
```

---

## Task 5: 集成测试

**Step 1: 测试完整安装流程**

运行: `python install.py`
预期:
- 同步脚本部署成功
- 索引生成器部署成功
- 定时任务配置成功
- 首次同步完成

**Step 2: 测试索引生成**

运行: `python ~/.claude/hooks/generate_index.py`
预期:
- 扫描备份目录
- 生成 `sessions.json`
- 输出会话数量

**Step 3: 验证索引内容**

打开: `{备份目录}/sessions.json`
预期:
- JSON 格式正确
- 包含 `generated_at`, `total_sessions`, `sessions` 字段
- 每个会话有 `file`, `date`, `time`, `project`, `topic`

**Step 4: 测试卸载**

运行: `python uninstall.py`
预期:
- hooks 移除
- 脚本删除
- 定时任务移除
- 备份文件保留

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `generate_index.py` | 新建 | 索引生成器脚本 |
| `install.py` | 修改 | 添加定时任务安装 |
| `README.txt` | 修改 | 添加索引功能说明 |
| `uninstall.py` | 新建 | 卸载脚本 |

---

## 提交计划

1. `feat: 添加会话索引生成器`
2. `feat: 安装脚本支持定时任务配置`
3. `docs: 更新README添加索引说明`
4. `feat: 添加卸载脚本`
