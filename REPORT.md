# 报告

## 完成情况

- 已实现机器人迎宾应用的核心状态机逻辑。
- 已实现 `PERSON_ENTERED`、`PERSON_LEFT`、`CONVERSATION_STARTED`、`CONVERSATION_ENDED`、`MEETING_STARTED`、`MEETING_ENDED`、`TICK` 的事件处理。
- 已实现 `snapshot()` 的防御性隔离。
- 已完成题目要求的单元测试，并在 Jupyter 中进行了手动验证。

## 测试命令

```bash
python -m unittest discover -s tests -p "test_*.py" -q
```

## 测试结果

- 7 个测试全部通过。

## Jupyter 手动验证

### 截图 1

![Jupyter 手动验证 1](outputs/jupyter-test-1.png)

### 截图 2

![Jupyter 手动验证 2](outputs/jupyter-test-2.png)

## 验证结论

### 1. 首次进入会触发迎宾

从截图 1 可以看到：

- `PERSON_ENTERED` 在空闲状态下会输出两个效果：
  - `ROBOT_ACTION: wave_hand`
  - `SPEECH: 欢迎光临`

这说明“空闲时有人进入，需要挥手并欢迎”的规则已经正确实现。

### 2. 同一会话内不会重复迎宾

截图 1 中后续的重复进入、对话开始、对话结束等事件都没有额外输出迎宾动作，说明：

- 同一个人在场期间不会重复迎宾
- 对话期间会抑制机器人动作

### 3. 离场 10 秒后由 `TICK` 触发送客

截图 1 中可以看到：

- `PERSON_LEFT` 不立即输出送客
- `TICK 14.0` 时没有输出
- `TICK 15.0` 时输出 `ROBOT_ACTION: send_off`

这和题目要求一致，说明离场超时逻辑正确。

### 4. `snapshot()` 不会被外部修改污染

截图 2 中先获取 `snap`，然后人为修改：

- `snap["present"] = False`
- `snap["current_person_id"] = "changed"`

随后再次调用 `app.snapshot()`，结果仍然保持原值，说明：

- `snapshot()` 返回的是隔离副本
- 外部修改不会影响内部状态

### 5. 自动化测试结果与手动验证一致

截图 2 还显示：

- `python -m unittest discover -s tests -p "test_*.py" -q`
- `Ran 7 tests in 0.000s`
- `OK`

这说明：

- Jupyter 的手动验证结果
- 自动化单元测试结果

两者是一致的，核心逻辑可认为已经通过验证。

## ROS 2 判断题说明

- 事实：应用层已经创建了一个 `ROBOT_ACTION` 类型的 `wave_hand` 效果。
- 事实：桥接层已经接受了一个异步任务。
- 事实：`ros2 action info` 显示没有 action server。
- 事实：`systemctl is-active robot-action.service` 显示服务未运行。

### 回答

1. 已经能证明什么
   - 能证明请求已经创建并交给了桥接层。
   - 不能证明下游 ROS 2 action server 已经在运行。

2. `accepted_async` 是否代表机器人已经完成挥手
   - 不能。它只代表异步请求被接受了。

3. 问题最可能在哪一层
   - 最可能在执行层、桥接层或 ROS 2 层，而不是应用层本身。

4. 下一步按什么顺序检查
   - 先检查 ROS 2 action server 是否运行。
   - 再检查桥接层是否能连到 action server。
   - 再检查机器人动作服务是否激活。
   - 最后检查硬件执行或 SDK 集成。

5. 当前能否直接执行真实动作，为什么
   - 不能。没有证据表明 action server 或 service 已经正常运行，所以不能直接认为真实动作可以执行。

## 已知限制

- 当前实现默认只考虑单个活跃访客会话。
- 对话或会议期间被抑制的送客动作，不会在结束后补发。
