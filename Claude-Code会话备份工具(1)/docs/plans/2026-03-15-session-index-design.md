# Claude Code 会话索引生成器设计文档

**日期**: 2026-03-15
**状态**: 已批准

## 背景

Claude Code 会话备份工具目前只保存原始 `.jsonl` 文件，文件名为 UUID 格式（如 `11043617-80fd-48d0-a58f-0998300168c6.jsonl`），难以通过文件名快速识别对话内容。

用户希望能够通过可读的文件名或索引来搜索历史对话。

## 需求

- 文件名或索引中包含**日期时间**
- 文件名或索引中包含**主题关键词**（从用户首条消息提取）
- 不影响同步脚本的**轻量快速**特性
- 便于搜索历史记录

## 设计方案

采用**两步式**架构：

### 第一步：快速同步（保持不变）

- **触发**: Hook（Stop / SessionEnd）
- **功能**: 增量同步 `.jsonl` 文件到备份目录
- **速度**: 1秒内完成
- **文件名**: 保持原始 UUID 格式

### 第二步：生成索引（新增）

- **触发**: 定时任务（如每天凌晨 2:00）
- **功能**: 扫描备份目录，提取会话信息，生成 JSON 索引
- **关键词提取**: 规则提取（无需 API 调用）

## 索引文件结构

**文件**: `{备份目录}/sessions.json`

```json
{
  "generated_at": "2026-03-15T10:00:00Z",
  "total_sessions": 35,
  "sessions": [
    {
      "file": "11043617-80fd-48d0-a58f-0998300168c6.jsonl",
      "date": "2026-03-04",
      "time": "13:50",
      "project": "java",
      "topic": "检测java环境是否已成功安装"
    }
  ]
}
```

### 字段说明

| 字段 | 来源 | 说明 |
|------|------|------|
| `file` | 原始文件名 | 用于定位实际会话文件 |
| `date` | `timestamp` 字段 | 对话日期 (YYYY-MM-DD) |
| `time` | `timestamp` 字段 | 对话时间 (HH:MM) |
| `project` | `cwd` 字段 | 项目/工作目录名 |
| `topic` | 用户首条消息 | 规则提取，最多30字符 |

## 规则提取逻辑

从 jsonl 文件中提取 `type="user"` 且 `parentUuid=null` 的首条用户消息：

1. 提取消息文本内容
2. 清理系统标签（如 `<ide_opened_file>...</ide_opened_file>`）
3. 去除首尾空白和标点
4. 截取前 30 个字符

**示例**:
- 输入: `随便写点代码让我检测java环境是否已经成功安装`
- 输出: `检测java环境是否已成功安装`

## 文件结构

```
Claude-Code会话备份工具(1)/
├── README.txt              # 更新说明
├── install.py              # 更新：安装定时任务
├── sync_raw_sessions.py    # 保持不变
├── generate_index.py       # 新增：索引生成器
└── uninstall.py            # 新增：卸载脚本（可选）
```

## 定时任务配置

### macOS (launchd)

创建 `~/Library/LaunchAgents/com.claude.session-index.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.session-index</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>/Users/{username}/.claude/hooks/generate_index.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>2</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
</dict>
</plist>
```

### Linux (cron)

```cron
0 2 * * * python3 ~/.claude/hooks/generate_index.py
```

## 使用方式

1. 运行 `python install.py` 安装（包含同步 + 索引生成器）
2. 每次对话结束 → 自动同步 jsonl 文件
3. 每天定时 → 自动生成/更新 `sessions.json` 索引
4. 需要搜索历史时 → 在 Claude Code 中询问：`"帮我在 {备份目录}/sessions.json 里搜索关于xxx的对话"`

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 定时任务失败 | 脚本内含错误处理，失败时记录日志 |
| jsonl 格式变化 | 提取逻辑使用宽松匹配，关键字段缺失时跳过 |
| 大量会话导致索引过大 | 索引仅包含必要字段，JSON 格式压缩高效 |

## 后续扩展（可选）

- [ ] 支持 Markdown 格式索引输出
- [ ] 支持按项目/日期过滤生成索引
- [ ] 集成 LLM API 智能提取摘要
