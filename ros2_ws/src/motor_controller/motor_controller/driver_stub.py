from __future__ import annotations

from dataclasses import dataclass

from autonomy_interfaces.contracts import MotorStatusMessage
from navigation.motion_adapter import MotorControlCommand


@dataclass(frozen=True)
class DriverState:
    mode: str
    forward_speed: float
    turn_rate: float
    left_wheel_speed: float
    right_wheel_speed: float
    brake: bool
    emergency_stop: bool


class MotorDriverStub:
    """Safe software-only stand-in for future motor hardware control."""

    def __init__(self) -> None:
        self.last_state = DriverState(
            mode="idle",
            forward_speed=0.0,
            turn_rate=0.0,
            left_wheel_speed=0.0,
            right_wheel_speed=0.0,
            brake=True,
            emergency_stop=False,
        )

    def apply(self, command: MotorControlCommand) -> MotorStatusMessage:
        self.last_state = DriverState(
            mode=command.mode,
            forward_speed=command.forward_speed,
            turn_rate=command.turn_rate,
            left_wheel_speed=command.left_wheel_speed,
            right_wheel_speed=command.right_wheel_speed,
            brake=command.brake,
            emergency_stop=command.emergency_stop,
        )
        return MotorStatusMessage(
            state="applied",
            mode=command.mode,
            applied=True,
            brake=command.brake,
            emergency_stop=command.emergency_stop,
            target_cell=(
                (command.target_row, command.target_col)
                if command.target_row is not None and command.target_col is not None
                else None
            ),
            applied_forward_speed=command.forward_speed,
            applied_turn_rate=command.turn_rate,
            left_wheel_speed=command.left_wheel_speed,
            right_wheel_speed=command.right_wheel_speed,
            goal_id=command.goal_id,
            sequence_id=command.sequence_id,
            detail=f"Stub driver applied mode={command.mode}.",
        )
