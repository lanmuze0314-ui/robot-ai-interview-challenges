# AI 使用说明

## 使用了什么 AI

- OpenAI Codex

## AI 帮了什么

- 帮助拆解题目，整理成状态机设计
- 帮助搭建 Python 包结构
- 帮助生成符合业务规则的测试
- 帮助撰写架构说明和报告说明

## 人工验证方式

- 人工检查实现逻辑
- 使用以下命令运行测试：

```bash
python -m unittest discover -s tests -p "test_*.py" -q
```

- 已确认测试全部通过
