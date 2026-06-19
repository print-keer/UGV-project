from __future__ import annotations

from dataclasses import dataclass

from autonomy_interfaces.contracts import MotionCommandMessage


@dataclass(frozen=True)
class DifferentialDriveConfig:
    track_width_m: float = 0.4
    max_wheel_speed: float = 1.0


@dataclass(frozen=True)
class MotorControlCommand:
    mode: str
    target_row: int | None
    target_col: int | None
    forward_speed: float
    turn_rate: float
    left_wheel_speed: float
    right_wheel_speed: float
    brake: bool
    emergency_stop: bool
    goal_id: str
    sequence_id: int


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def differential_drive_wheel_speeds(
    forward_speed: float,
    turn_rate: float,
    config: DifferentialDriveConfig,
) -> tuple[float, float]:
    half_track = config.track_width_m / 2.0
    left = forward_speed - turn_rate * half_track
    right = forward_speed + turn_rate * half_track
    return (
        _clamp(left, config.max_wheel_speed),
        _clamp(right, config.max_wheel_speed),
    )


def to_motor_control_command(
    command: MotionCommandMessage,
    config: DifferentialDriveConfig | None = None,
) -> MotorControlCommand:
    config = config or DifferentialDriveConfig()
    target_row = command.target_cell[0] if command.target_cell is not None else None
    target_col = command.target_cell[1] if command.target_cell is not None else None

    if command.command_type == "emergency_stop":
        return MotorControlCommand(
            mode="emergency_stop",
            target_row=target_row,
            target_col=target_col,
            forward_speed=0.0,
            turn_rate=0.0,
            left_wheel_speed=0.0,
            right_wheel_speed=0.0,
            brake=True,
            emergency_stop=True,
            goal_id=command.goal_id,
            sequence_id=command.sequence_id,
        )

    if command.command_type in {"hold_position", "stop_at_goal"} or command.stop:
        return MotorControlCommand(
            mode="hold",
            target_row=target_row,
            target_col=target_col,
            forward_speed=0.0,
            turn_rate=0.0,
            left_wheel_speed=0.0,
            right_wheel_speed=0.0,
            brake=True,
            emergency_stop=False,
            goal_id=command.goal_id,
            sequence_id=command.sequence_id,
        )

    forward_speed = max(0.0, float(command.linear_velocity))
    turn_rate = float(command.angular_velocity)
    left_wheel_speed, right_wheel_speed = differential_drive_wheel_speeds(
        forward_speed,
        turn_rate,
        config,
    )
    return MotorControlCommand(
        mode="track_cell",
        target_row=target_row,
        target_col=target_col,
        forward_speed=forward_speed,
        turn_rate=turn_rate,
        left_wheel_speed=left_wheel_speed,
        right_wheel_speed=right_wheel_speed,
        brake=False,
        emergency_stop=False,
        goal_id=command.goal_id,
        sequence_id=command.sequence_id,
    )
