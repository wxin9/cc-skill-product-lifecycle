---
name: kimi-delegate
description: 将任务委派给腾讯云服务器上的 Claude Code（背后接 Kimi K2.5 推理模型）。当用户说"让 Kimi 帮我"、"发给 Kimi 做"、"委派给腾讯云"、"用 Kimi 做"、"/delegate-kimi"、"/kimi-delegate"时触发。也适合 Claude 自主判断任务属于文案草稿、代码生成、数据分析、批处理脚本等初级事务型任务、且不需要访问本地文件时使用。
---

# Kimi 委派操作手册

## 基础设施

| 项目 | 值 |
|------|-----|
| 服务器 | `ubuntu@101.34.67.157` |
| SSH 密钥 | `/home/ubuntu/projects/ssh/tencent_server.pem` |
| Claude Code 路径 | `/root/.nvm/versions/node/v22.22.1/bin/claude` |
| 代理地址 | `http://localhost:4000`（kimi-proxy 服务，仅本机） |
| 后端模型 | Kimi K2.5（Moonshot 推理模型） |

## 核心原则：任务独立，走子 Agent

Kimi K2.5 是推理模型，响应较慢（30~120 秒），**必须通过 Agent 工具以 `run_in_background=true` 派发子 agent**，主对话继续响应用户，子 agent 跑完自动通知。

## 调用模板

### 单任务

```
description: "Kimi: <简短任务描述>"
subagent_type: general-purpose
run_in_background: true
prompt: |
  用 Bash 工具执行以下命令（直接等待结果，不要在内部再用 run_in_background）：

  TASK_B64=$(echo -n "<完整任务描述，含所有必要上下文>" | base64 -w0)
  ssh -i /home/ubuntu/projects/ssh/tencent_server.pem \
      -o StrictHostKeyChecking=no \
      -o ConnectTimeout=15 \
      ubuntu@101.34.67.157 \
      "sudo bash -c 'export PATH=/root/.nvm/versions/node/v22.22.1/bin:\$PATH && \
       ANTHROPIC_BASE_URL=http://localhost:4000 \
       ANTHROPIC_API_KEY=sk-proxy-local \
       CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
       claude -p \"\$(echo ${TASK_B64} | base64 -d)\"'" 2>/dev/null

  Bash timeout 设为 300000ms（5分钟）。
  若返回 429（engine_overloaded），等待 10 秒后重试一次。
  命令完成后，直接返回输出内容。
```

**技术说明**：`${TASK_B64}` 在本地 shell 展开为 base64 字符串（安全，无特殊字符）；`\$PATH` 和 `\$(...)` 中的反斜杠让它们保留到远端 bash 再展开。

### 多任务并发

同一条消息内发出多个 Agent 调用（均 `run_in_background=true`），子 agent 并行执行，各自完成后分别通知。

## 任务描述要写完整

Kimi 没有本地上下文，任务描述必须自包含——把所有必要信息内嵌进去：

- **好**：`为一篇关于索尼 A7CM2 夜景摄影技巧的小红书帖子写3个吸引人的标题，要求口语化，带emoji，适合25岁女性用户`
- **差**：`帮我写标题`（没有上下文）

## 适合委派给 Kimi 的任务

- 文案草稿、标题生成、话题标签
- 代码片段生成（功能明确、不需要读本地文件）
- 数据格式化、内容整理
- 批处理脚本模板
- 通用知识查询、分析报告

## 不适合委派的任务

- 需要读写本地文件或项目代码
- 需要多轮交互或积累上下文
- 代码调试、错误排查
- 任何需要工具调用的任务（`-p` 是单次问答模式）

## 完整执行流程

1. **整理任务描述**：提炼清晰的一段话，把所有上下文内嵌
2. **构造 base64 命令**：用 `echo -n "..." | base64 -w0` 编码，避免特殊字符破坏 SSH 引号
3. **派发子 agent**（`run_in_background=true`），告诉用户"已发给 Kimi，结果来了通知你"
4. **收到子 agent 通知**后，把结果展示给用户，必要时做二次加工
