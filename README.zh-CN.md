[English](README.md) | [中文](README.zh-CN.md)

# Product Lifecycle

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/wxin9/cc-skill-product-lifecycle)](https://github.com/wxin9/cc-skill-product-lifecycle/releases)

> **脚本编排 + 交互暂停**的产品全生命周期管理 — orchestrator 自动执行 Phase 序列，在交互节点暂停，通知模型处理，然后恢复

## ⚠ 破坏性变更 (v2.0)

**所有旧命令已移除**：
- ❌ \`./lifecycle init\` → **已移除**
- ❌ \`./lifecycle validate\` → **已移除**
- ❌ \`./lifecycle draft\` → **已移除**
- ❌ \`./lifecycle plan\` → **已移除**
- ❌ 所有其他旧命令 → **已移除**

**新命令**：
- ✅ \`./orchestrator run --intent <intent> --user-input "<输入>"\` — 启动编排
- ✅ \`./orchestrator resume --from-phase <phase-id>\` — 从暂停状态恢复
- ✅ \`./orchestrator status\` — 显示状态
- ✅ \`./orchestrator cancel\` — 取消工作流

**迁移**：Orchestrator 会自动迁移旧的 \`steps/\` 格式到 \`checkpoint.json\`。参见下方的迁移指南。

## 🎯 核心价值

**解决的问题**：
- ❌ 模型驱动工作流：模型中途失忆，后续脚本不执行
- ❌ 手动步骤执行：用户必须知道下一步命令
- ❌ 无交互处理：模型无法暂停等待用户输入
- ❌ 无失败恢复：验证失败阻塞整个工作流

**解决方案**：
- ✅ **脚本编排引擎**：Orchestrator 自动执行 Phase 序列
- ✅ **交互暂停**：Orchestrator 在用户审核/访谈节点暂停，通知模型
- ✅ **失败恢复**：验证/DoD 失败暂停工作流，模型修复后恢复
- ✅ **状态持久化**：Checkpoint 记录 Phase 级别状态，支持从断点恢复

## ⭐ v2.0.0 新特性

### 1. Orchestrator 引擎
- **脚本编排工作流**：根据意图自动执行 Phase 序列
- **状态机**：Phase 级别状态转换，依赖检查
- **无需模型记忆**：Orchestrator 处理整个工作流，模型只需响应通知

### 2. 交互暂停
- **自动暂停**：Orchestrator 在用户审核/访谈节点暂停
- **双重通知**：stdout + \`.lifecycle/notification.json\`
- **恢复支持**：模型修复问题后调用 \`resume\` 继续

### 3. 失败恢复
- **验证失败**：Orchestrator 暂停，模型修复后重试
- **DoD 失败**：Orchestrator 暂停，模型解决后继续
- **重试策略**：每个 Phase 可配置重试次数

### 4. Checkpoint 管理器
- **Phase 级别状态**：记录已完成 Phase、当前 Phase、Phase 数据
- **自动迁移**：迁移旧版 \`steps/\` 格式到 \`checkpoint.json\`
- **断点恢复**：加载 checkpoint 从暂停 Phase 继续

### 5. 意图解析器
- **正则匹配**：基于模式的意图识别
- **优先级排序**：Bug-fix (1) > PRD-change (3) > New-product (9)
- **复合意图**：按顺序处理多个意图

## 🚀 快速开始

### 安装

\`\`\`bash
# 克隆仓库
git clone https://github.com/wxin9/cc-skill-product-lifecycle.git

# 安装为 Claude Code 技能
cp -r cc-skill-product-lifecycle ~/.claude/skills/product-lifecycle
\`\`\`

### 使用（Orchestrator 命令）

安装后，使用 orchestrator 命令：

\`\`\`bash
# 启动新产品工作流
./orchestrator run --intent new-product --user-input "我想做一个任务管理工具"

# Orchestrator 会：
# 1. 执行 Phase 1（自动）— 创建文档结构
# 2. 在 Phase 2 暂停 — 通知模型："等待 PRD 审核"
# 3. 模型生成 PRD 草案
# 4. 恢复：./orchestrator resume --from-phase phase-2-draft-prd
# 5. 继续 Phase 3-9...
\`\`\`

**示例对话**：

\`\`\`
你："我想做一个任务管理工具"
Claude: [调用 ./orchestrator run --intent new-product]
        [Orchestrator 在 Phase 2 暂停]
        [通知："等待 PRD 审核"]
        [Claude 生成 PRD 草案]
        [调用 ./orchestrator resume]

你："需求变了，要加支付功能"
Claude: [调用 ./orchestrator run --intent prd-change]
        [Orchestrator 执行 Phase 10 → Phase 2 → Phase 3...]
\`\`\`

## 💡 核心功能

| 功能 | 说明 |
|------|------|
| **AI 协作起草** | Claude 主动起草 PRD/架构，你做审稿人 |
| **脚本强制门控** | \`sys.exit(1)\` 物理阻断，无法跳步 |
| **复合意图识别** | "修了 bug 顺便调整需求" — 识别多个意图，排序执行 |
| **项目类型自动识别** | 5 种类型，测试维度自适应 |
| **自动快照 & Diff** | 验证通过自动快照，变更时自动对比 |
| **Velocity 追踪** | 估算 vs 实际工时 + ASCII 趋势图 |
| **DoD 门控扩展** | lint/覆盖率/代码审查，warn 或 fail |
| **ADR 管理** | 架构决策记录全生命周期管理 |
| **风险登记册** | 概率×影响矩阵自动评级 |
| **Sprint Review** | 门控通过自动生成评审材料 |

## 📖 工作流程

\`\`\`
Phase 0: 意图识别
   ↓
Phase 1: 项目初始化 → DoD/Risk/ADR 初始化
   ↓
Phase 2: AI 起草 PRD → 你审核修改
   ↓
Phase 3: 验证 PRD → 自动快照
   ↓
Phase 4: 架构访谈
   ↓
Phase 5: AI 起草架构 → 包含 ADR 初稿
   ↓
Phase 6: 验证架构 → 自动快照
   ↓
Phase 7: 生成测试图谱 + 自适应大纲
   ↓
Phase 8: 规划迭代 → Velocity 估算
   ↓
Phase 9: 执行迭代 → 4 层门控验证
   ↓
Phase 10: 处理变更 → 图谱遍历级联更新
\`\`\`

## 🛠️ 常用命令

\`\`\`bash
# 启动编排
./orchestrator run --intent new-product --user-input "我想做一个产品"

# 从暂停状态恢复
./orchestrator resume --from-phase phase-2-draft-prd

# 显示状态
./orchestrator status

# 取消工作流
./orchestrator cancel
\`\`\`

**旧命令（v2.0 已移除）**：
- ~~\`python -m scripts init\`~~ → 使用 \`./orchestrator run --intent new-product\`
- ~~\`python -m scripts validate\`~~ → Orchestrator 自动验证
- ~~\`python -m scripts draft\`~~ → Orchestrator 自动起草
- ~~\`python -m scripts plan\`~~ → Orchestrator 自动规划
- ~~所有其他旧命令~~ → 使用 orchestrator 命令

## 📊 生成的项目结构

\`\`\`
Docs/
├── product/PRD.md          # PRD 文档
├── tech/ARCH.md            # 架构文档
├── tests/MASTER_OUTLINE.md # 测试大纲
└── iterations/iter-N/      # 迭代计划 + 测试记录 + Sprint Review

.lifecycle/
├── test_graph.json         # 测试知识图谱 ⭐ v1.1.0
├── config.json             # 项目配置
├── dod.json                # DoD 规则
├── risk_register.json      # 风险登记册
├── velocity.json           # Velocity 追踪
└── snapshots/              # 文档快照
\`\`\`

## 🎓 模型兼容性

- **推荐**：Claude Sonnet 4+ — 最佳起草质量
- **可用**：Claude Haiku — 可完成完整工作流，起草质量稍低
- **核心机制**：Orchestrator 处理工作流，模型只需响应通知

## 🔄 迁移指南（从 v1.0）

### 步骤 1：备份现有项目

\`\`\`bash
cp -r myproject myproject_backup
\`\`\`

### 步骤 2：更新技能

\`\`\`bash
cd ~/.claude/skills/product-lifecycle
git pull origin main
# 或从 GitHub 重新下载
\`\`\`

### 步骤 3：运行迁移

Orchestrator 会自动迁移旧版 \`steps/\` 格式到 \`checkpoint.json\`：

\`\`\`bash
./orchestrator status
# 输出：
# ⚠ 正在从旧版 steps/ 格式迁移...
# ✓ 从旧版格式迁移了 5 个 Phase
\`\`\`

### 步骤 4：验证迁移

\`\`\`bash
./orchestrator status
# 应显示：
# 状态：migrated
# 已完成 Phase：[phase-1-init, phase-3-validate-prd, ...]
\`\`\`

### 步骤 5：使用新命令

所有旧命令已移除。使用 orchestrator 命令：

| 旧命令 | 新命令 |
|--------|--------|
| \`./lifecycle init\` | \`./orchestrator run --intent new-product\` |
| \`./lifecycle validate\` | Orchestrator 自动验证 |
| \`./lifecycle draft prd\` | Orchestrator 在 Phase 2 自动起草 |
| \`./lifecycle plan\` | Orchestrator 在 Phase 8 自动规划 |
| \`./lifecycle gate --iteration 1\` | Orchestrator 在 Phase 9 自动门控 |
| \`./lifecycle change prd\` | \`./orchestrator run --intent prd-change\` |

### 故障排除

**问题**：迁移失败

**解决方案**：
1. 检查 \`.lifecycle/steps/\` 目录是否存在
2. 检查步骤文件是否为有效 JSON
3. 手动删除 \`.lifecycle/checkpoint.json\` 并重新运行 \`./orchestrator status\`

**问题**：恢复不工作

**解决方案**：
1. 检查 \`.lifecycle/checkpoint.json\` 是否存在
2. 检查 \`current_phase\` 字段是否设置
3. 检查 \`.lifecycle/notification.json\` 是否存在

## 📄 许可证

Apache License 2.0 — 见 [LICENSE](LICENSE)

## 🏢 商业使用

商业使用请在产品文档中注明出处：

\`\`\`
本产品使用 Product-Lifecycle Skill (https://github.com/wxin9/cc-skill-product-lifecycle)
Copyright 2026 Kaiser (wxin966@gmail.com)
Apache License 2.0
\`\`\`

---

**完整变更日志**：[CHANGELOG.md](CHANGELOG.md) | **GitHub**：[wxin9/cc-skill-product-lifecycle](https://github.com/wxin9/cc-skill-product-lifecycle)
