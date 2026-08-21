# 报告

## 完成情况

- 已实现机器人迎宾应用的核心逻辑
- 已实现 `PERSON_ENTERED`、`PERSON_LEFT`、`CONVERSATION_STARTED`、`CONVERSATION_ENDED`、`MEETING_STARTED`、`MEETING_ENDED`、`TICK` 的事件状态机
- 已实现 `snapshot()` 隔离
- 已补充题目要求的测试场景

## 测试命令

```bash
python -m unittest discover -s tests -p "test_*.py" -q
```

## 测试结果

- 7 个测试全部通过

## ROS 2 判断题说明

- 事实：应用层已经创建了一个 `ROBOT_ACTION` 类型的 `wave_hand` 效果
- 事实：桥接层已经接受了一个异步任务
- 事实：`ros2 action info` 显示没有 action server
- 事实：`systemctl is-active robot-action.service` 显示服务未运行

### 答案

1. 已经能证明什么
   - 能证明请求已经创建并交给了桥接层
   - 不能证明下游 ROS 2 action server 已经在运行

2. `accepted_async` 是否代表机器人已经完成挥手
   - 不能。它只代表异步请求被接受了

3. 问题最可能在哪一层
   - 最可能在执行层、桥接层或 ROS 2 层，而不是应用层本身

4. 下一步按什么顺序检查
   - 先检查 ROS 2 action server 是否运行
   - 再检查桥接层是否能连到 action server
   - 再检查机器人动作服务是否激活
   - 最后检查硬件执行或 SDK 集成

5. 当前能否直接执行真实动作，为什么
   - 不能。没有证据表明 action server 或 service 已经正常运行，所以不能直接认为真实动作可以执行

## 已知限制

- 该实现默认只考虑单个活跃访客会话
- 对话或会议期间被抑制的送客动作，不会在结束后补发
