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
