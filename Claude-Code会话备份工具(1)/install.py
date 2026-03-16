"""
Claude Code 会话备份 - 一键安装脚本
运行方式：python install.py
"""
import sys
import os
import json
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print()
print("=" * 50)
print("  Claude Code 会话录像自动备份 - 安装程序")
print("=" * 50)
print()

# ==================== Step 1: 检测环境 ====================

home = Path.home()
claude_dir = home / ".claude"
hooks_dir = claude_dir / "hooks"
settings_path = claude_dir / "settings.json"
projects_dir = claude_dir / "projects"

# 检查 Claude Code 是否安装
if not claude_dir.exists():
    print("❌ 未找到 Claude Code 配置目录：" + str(claude_dir))
    print("   请先安装并运行一次 Claude Code，再执行此脚本。")
    input("按回车退出...")
    sys.exit(1)

if not projects_dir.exists():
    print("❌ 未找到会话目录：" + str(projects_dir))
    print("   请先用 Claude Code 进行至少一次对话，再执行此脚本。")
    input("按回车退出...")
    sys.exit(1)

# 统计现有会话
jsonl_count = len(list(projects_dir.rglob("*.jsonl")))
print(f"✓ 检测到 Claude Code 配置目录：{claude_dir}")
print(f"✓ 发现 {jsonl_count} 个历史会话文件")
print()

# ==================== Step 2: 选择备份目录 ====================

default_backup = home / "Documents" / "claude-sessions-backup"

print("请输入备份目录路径。")
print("建议使用有云同步的目录（OneDrive、坚果云等），这样即使电脑坏了云端也有。")
print(f"直接回车使用默认值：{default_backup}")
print()

user_input = input("备份目录: ").strip()
if not user_input:
    backup_dir = default_backup
else:
    backup_dir = Path(user_input)

try:
    backup_dir.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"❌ 无法创建备份目录：{e}")
    input("按回车退出...")
    sys.exit(1)

print(f"✓ 备份目录：{backup_dir}")
print()

# ==================== Step 2.5: 配置 AI 主题提取（可选） ====================

print("是否配置 AI 主题提取功能？")
print("· 配置后，索引生成器会使用 AI 智能提取对话主题")
print("· 不配置则使用简单方式（截取前30个字）")
print()

ai_config = {"api_key": "", "api_base": "https://api.openai.com/v1", "model": "gpt-4o-mini"}

enable_ai = input("启用 AI 主题提取？(y/N): ").strip().lower()
if enable_ai == 'y':
    print()
    print("请选择 AI 服务商：")
    print("  1. OpenAI")
    print("  2. DeepSeek")
    print("  3. 智谱 GLM")
    print("  4. 自定义（OpenAI 兼容接口）")
    print()

    choice = input("请输入选项 (1-4): ").strip()

    if choice == "1":
        ai_config["api_base"] = "https://api.openai.com/v1"
        ai_config["model"] = "gpt-4o-mini"
    elif choice == "2":
        ai_config["api_base"] = "https://api.deepseek.com/v1"
        ai_config["model"] = "deepseek-chat"
    elif choice == "3":
        ai_config["api_base"] = "https://open.bigmodel.cn/api/paas/v4"
        ai_config["model"] = "glm-4-flash"
    elif choice == "4":
        print()
        custom_base = input("请输入 API Base URL: ").strip()
        custom_model = input("请输入模型名称 (默认 gpt-4o-mini): ").strip()
        ai_config["api_base"] = custom_base if custom_base else "https://api.openai.com/v1"
        ai_config["model"] = custom_model if custom_model else "gpt-4o-mini"

    print()
    api_key = input("请输入 API Key: ").strip()
    if api_key:
        ai_config["api_key"] = api_key
        print(f"✓ AI 配置完成：{ai_config['model']} @ {ai_config['api_base']}")
    else:
        print("⚠️ 未输入 API Key，将使用简单方式提取主题")
        ai_config["api_key"] = ""
else:
    print("→ 跳过 AI 配置，将使用简单方式提取主题")

print()

# ==================== Step 3: 部署同步脚本 ====================

hooks_dir.mkdir(parents=True, exist_ok=True)

# 读取模板脚本，替换路径
script_dir = Path(__file__).parent
template_path = script_dir / "sync_raw_sessions.py"

if not template_path.exists():
    print(f"❌ 未找到同步脚本模板：{template_path}")
    input("按回车退出...")
    sys.exit(1)

try:
    with open(template_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # 转义路径中的反斜杠，避免替换问题
    src_dir_escaped = str(projects_dir).replace("\\", "\\\\")
    dst_dir_escaped = str(backup_dir).replace("\\", "\\\\")

    script_content = script_content.replace("__SRC_DIR__", src_dir_escaped)
    script_content = script_content.replace("__DST_DIR__", dst_dir_escaped)

    deploy_path = hooks_dir / "sync_raw_sessions.py"
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
except Exception as e:
    print(f"❌ 部署同步脚本失败：{e}")
    input("按回车退出...")
    sys.exit(1)

print(f"✓ 同步脚本已部署到：{deploy_path}")

# ==================== Step 4: 配置 hooks ====================

def add_hook_to_settings(hooks_dict, hook_name, hook_entry):
    """
    安全地将 hook 添加到 settings 中

    Args:
        hooks_dict: settings 中的 hooks 字典
        hook_name: hook 名称 (如 "Stop", "SessionEnd")
        hook_entry: 要添加的 hook 条目
    """
    existing_hooks = hooks_dict.get(hook_name, [])

    # 收集所有已存在的命令
    existing_commands = set()
    for group in existing_hooks:
        if isinstance(group, dict) and "hooks" in group:
            for h in group["hooks"]:
                if isinstance(h, dict) and "command" in h:
                    existing_commands.add(h["command"])

    # 如果命令已存在，不需要添加
    if hook_entry["command"] in existing_commands:
        return

    # 查找或创建第一个可用的 group
    if not existing_hooks:
        # 没有任何 hook，创建新的 group
        hooks_dict[hook_name] = [{"hooks": [hook_entry]}]
    else:
        # 找到第一个有 "hooks" 键的 group
        target_group = None
        for group in existing_hooks:
            if isinstance(group, dict) and "hooks" in group:
                target_group = group
                break

        if target_group:
            target_group["hooks"].append(hook_entry)
        else:
            # 没有合适的 group，创建新的
            existing_hooks.append({"hooks": [hook_entry]})

        hooks_dict[hook_name] = existing_hooks

try:
    # 读取现有 settings.json
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})

    sync_command = "PYTHONIOENCODING=utf-8 python ~/.claude/hooks/sync_raw_sessions.py"

    # Stop hook - 每轮对话结束触发
    stop_hook_entry = {"type": "command", "command": sync_command}
    add_hook_to_settings(hooks, "Stop", stop_hook_entry)

    # SessionEnd hook - 会话结束时触发，给足够的时间完成同步
    # timeout 单位为毫秒，30000ms = 30秒
    session_end_hook_entry = {
        "type": "command",
        "command": sync_command,
        "timeout": 30000
    }
    add_hook_to_settings(hooks, "SessionEnd", session_end_hook_entry)

    # 写回 settings.json（原子性写入）
    temp_settings_path = settings_path.with_suffix('.json.tmp')
    with open(temp_settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
    temp_settings_path.replace(settings_path)

    print(f"✓ Hook 已配置到：{settings_path}")
    print("  · Stop hook（每轮对话结束自动备份）")
    print("  · SessionEnd hook（关窗口时兜底备份，超时30秒）")
    print()
except Exception as e:
    print(f"❌ 配置 hooks 失败：{e}")
    input("按回车退出...")
    sys.exit(1)

# ==================== Step 4.5: 部署索引生成器并配置定时任务 ====================

print()
print("正在配置索引生成器...")

def setup_scheduled_indexer(backup_dir, hooks_dir, ai_config):
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

        # 替换 AI 配置
        script_content = script_content.replace('AI_API_KEY = ""', f'AI_API_KEY = "{ai_config["api_key"]}"')
        script_content = script_content.replace('AI_API_BASE = "https://api.openai.com/v1"', f'AI_API_BASE = "{ai_config["api_base"]}"')
        script_content = script_content.replace('AI_MODEL = "gpt-4o-mini"', f'AI_MODEL = "{ai_config["model"]}"')

        deploy_path = hooks_dir / "generate_index.py"
        with open(deploy_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"✓ 索引生成器已部署到: {deploy_path}")
        if ai_config["api_key"]:
            print(f"  AI 主题提取已启用: {ai_config['model']}")
    except Exception as e:
        print(f"⚠️ 部署索引生成器失败: {e}")
        return False

    # 配置定时任务
    system = sys.platform

    if system == "darwin":
        # macOS: 使用 launchd
        return setup_launchd(hooks_dir)
    elif system.startswith("linux"):
        # Linux: 使用 cron
        return setup_cron(hooks_dir)
    else:
        print(f"⚠️ 不支持的系统: {system}")
        print("   请手动配置定时任务")
        return False


def setup_launchd(hooks_dir):
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


setup_scheduled_indexer(backup_dir, hooks_dir, ai_config)

# ==================== Step 5: 首次全量同步 ====================

print()
print("正在执行首次全量同步...")

try:
    # 直接调用同步逻辑
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_raw_sessions", deploy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.sync()
except Exception as e:
    print(f"⚠️ 首次同步出现警告：{e}")
    print("   这可能是正常的，后续会自动重试。")

# 统计备份结果
try:
    backup_count = len(list(backup_dir.rglob("*.jsonl")))
    backup_size_mb = sum(f.stat().st_size for f in backup_dir.rglob("*.jsonl")) / 1024 / 1024
except Exception:
    backup_count = 0
    backup_size_mb = 0

print()
print("=" * 50)
print(f"  ✅ 部署完成！")
print(f"  已备份 {backup_count} 个会话，共 {backup_size_mb:.1f} MB")
print(f"  备份位置：{backup_dir}")
print("=" * 50)
print()
print("从现在起，每次用 Claude Code 对话：")
print("  · 每轮结束 → 自动备份（无感知）")
print("  · 关窗口 → 再备份一次（防漏）")
print()
print("想找历史记录？在 Claude Code 里直接问：")
print(f'  "帮我在 {backup_dir} 里搜索关于xxx的历史对话"')
print()

input("按回车退出...")
