# Report

## Completion Status

- Implemented the core robot greeting application.
- Implemented the event-driven state machine for enter, leave, conversation, meeting, and tick handling.
- Implemented snapshot isolation.
- Added tests for the required scenarios.

## Test Command

```bash
python -m unittest discover -s tests -p "test_*.py" -q
```

## Test Result

- 7 tests passed.

## ROS 2 Judgment Notes

- Fact: The application created a `ROBOT_ACTION` effect with `wave_hand`.
- Fact: The bridge accepted an asynchronous task.
- Fact: `ros2 action info` showed no action server.
- Fact: `systemctl is-active robot-action.service` reported inactive.

### Answers

1. What is already proven
   - The request was created and handed to the bridge.
   - The downstream ROS 2 action server was not confirmed to be running.

2. Does `accepted_async` mean the robot has already waved
   - No. It only means the async request was accepted.

3. Most likely problem layer
   - The problem is most likely in the execution/bridge/ROS 2 layer, not in the application layer that created the effect.

4. Next inspection order
   - Check whether the ROS 2 action server is running.
   - Check whether the bridge can reach the action server.
   - Check whether the robot action service is active.
   - Then verify hardware execution or SDK integration.

5. Can the real action be executed now
   - No. There is no evidence that the action server or service is active, so the real robot action cannot be assumed to be executable.

## Known Limits

- The implementation assumes a single active visitor session at a time.
- Suppressed departures are intentionally not backfilled after conversation or meeting periods.
