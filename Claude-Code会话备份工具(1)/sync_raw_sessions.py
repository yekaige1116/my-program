"""
Claude Code 会话原始 jsonl 增量同步脚本
- 将 .claude/projects/ 下所有 .jsonl 原样复制到指定备份目录
- 增量：只复制新增或变化的文件（基于大小和修改时间）
- 轻量：1秒内完成，适合 hook 自动触发
- 安全：原子性写入，错误不会损坏状态

由 install.py 自动部署，路径会被替换为实际值。
手动使用时请修改下方 SRC_DIR 和 DST_DIR。
"""
import sys
import os
import shutil
import json
import tempfile
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# === 以下两行路径由 install.py 自动替换 ===
SRC_DIR = Path(r"__SRC_DIR__")
DST_DIR = Path(r"__DST_DIR__")
# === 路径配置结束 ===

SYNC_LOG = DST_DIR / ".sync_state.json"


def load_sync_state():
    """加载同步状态，失败时返回空字典"""
    if SYNC_LOG.exists():
        try:
            with open(SYNC_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # 状态文件损坏或无法读取，从头开始同步
            print(f"⚠️ 状态文件损坏，将执行完整同步：{e}")
            return {}
    return {}


def save_sync_state(state):
    """
    原子性保存同步状态
    先写入临时文件，再原子性地重命名，避免写入中途崩溃导致文件损坏
    """
    try:
        DST_DIR.mkdir(parents=True, exist_ok=True)
        # 在同一目录下创建临时文件，确保同一文件系统（rename 才是原子的）
        temp_fd, temp_path = tempfile.mkstemp(
            dir=DST_DIR,
            prefix=".sync_state_",
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            # 原子性替换
            os.replace(temp_path, SYNC_LOG)
        except Exception:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    except Exception as e:
        print(f"⚠️ 保存状态文件失败：{e}")


def get_file_signature(file_path):
    """
    获取文件签名（大小 + 修改时间）
    用于判断文件是否变化
    """
    try:
        stat = file_path.stat()
        return {
            "size": stat.st_size,
            "mtime": stat.st_mtime
        }
    except OSError:
        return None


def sync():
    """
    执行增量同步

    - 复制新增或变化的文件
    - 跳过未变化的文件
    - 可选：清理备份目录中已不存在于源目录的文件
    """
    try:
        DST_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ 无法创建备份目录：{e}")
        return

    state = load_sync_state()
    copied = 0
    skipped = 0
    errors = 0

    # 收集当前源目录中的所有文件
    current_files = set()

    try:
        src_files = list(SRC_DIR.rglob("*.jsonl"))
    except Exception as e:
        print(f"❌ 无法扫描源目录：{e}")
        return

    for src_path in src_files:
        try:
            rel_path = src_path.relative_to(SRC_DIR)
            key = str(rel_path)
            current_files.add(key)

            dst_path = DST_DIR / rel_path
            signature = get_file_signature(src_path)

            if signature is None:
                errors += 1
                continue

            # 检查是否需要同步
            if key in state:
                old_sig = state[key]
                # 比较大小和修改时间
                if (old_sig.get("size") == signature["size"] and
                    old_sig.get("mtime") == signature["mtime"]):
                    skipped += 1
                    continue

            # 执行复制
            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_path), str(dst_path))
                state[key] = signature
                copied += 1
            except Exception as e:
                print(f"⚠️ 复制失败 {rel_path}：{e}")
                errors += 1

        except Exception as e:
            errors += 1
            continue

    # 清理已删除的文件（备份目录中存在但源目录中已不存在的文件）
    removed = 0
    stale_keys = set(state.keys()) - current_files
    for key in stale_keys:
        try:
            dst_path = DST_DIR / key
            if dst_path.exists():
                dst_path.unlink()
                removed += 1
            del state[key]
        except Exception as e:
            print(f"⚠️ 清理失败 {key}：{e}")

    # 保存状态
    save_sync_state(state)

    # 输出结果
    if copied > 0 or removed > 0 or errors > 0:
        msg_parts = []
        if copied > 0:
            msg_parts.append(f"复制 {copied} 个")
        if skipped > 0:
            msg_parts.append(f"跳过 {skipped} 个")
        if removed > 0:
            msg_parts.append(f"清理 {removed} 个")
        if errors > 0:
            msg_parts.append(f"错误 {errors} 个")
        print(f"同步完成：" + "，".join(msg_parts))


if __name__ == '__main__':
    sync()
