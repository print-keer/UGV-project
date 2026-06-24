from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    MissionStateMessage,
    MotionCommandMessage,
    MotorStatusMessage,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
    SensorObservationMessage,
)
from autonomy_interfaces.serialization import deserialize_message, serialize_message


class ContractSerializationTests(unittest.TestCase):
    def test_occupancy_grid_round_trip(self) -> None:
        original = OccupancyGridMessage(
            width=2,
            height=2,
            resolution=1.0,
            origin=(1, 2),
            data=[0, 1, 2, 0],
            source_map="unit",
            revision=3,
        )

        restored = deserialize_message(serialize_message(original), OccupancyGridMessage)

        self.assertEqual(restored, original)

    def test_goal_and_path_round_trip(self) -> None:
        goal = MissionGoalMessage(start_cell=(0, 0), goal_cell=(3, 4), goal_id="goal_a")
        path = PlannedPathMessage(path_found=True, waypoints=[(0, 0), (0, 1)], total_cost=1.0, goal_id="goal_a")

        self.assertEqual(deserialize_message(serialize_message(goal), MissionGoalMessage), goal)
        self.assertEqual(deserialize_message(serialize_message(path), PlannedPathMessage), path)

    def test_extended_status_round_trip(self) -> None:
        planner_status = PlannerStatusMessage(
            state="success",
            message="Path found.",
            goal_id="goal_a",
            visited_nodes=11,
            start_cell=(0, 0),
            goal_cell=(2, 2),
            occupancy_revision=3,
        )
        navigation_status = NavigationStatusMessage(
            state="following_path",
            message="Accepted path.",
            current_cell=(2, 2),
            current_waypoint_index=4,
            goal_id="goal_a",
            path_length=5,
        )
        replan_request = ReplanRequestMessage(
            reason="path_blocked",
            current_cell=(1, 1),
            goal_id="goal_a",
            occupancy_revision=3,
        )

        self.assertEqual(
            deserialize_message(serialize_message(planner_status), PlannerStatusMessage),
            planner_status,
        )
        self.assertEqual(
            deserialize_message(serialize_message(navigation_status), NavigationStatusMessage),
            navigation_status,
        )
        self.assertEqual(
            deserialize_message(serialize_message(replan_request), ReplanRequestMessage),
            replan_request,
        )

    def test_sensor_observation_round_trip(self) -> None:
        observation = SensorObservationMessage(
            sensor_type="lidar",
            detected_cells=[(1, 2), (2, 2)],
            source_map="unit_map",
            sequence_id=4,
        )

        self.assertEqual(
            deserialize_message(serialize_message(observation), SensorObservationMessage),
            observation,
        )

    def test_motion_command_round_trip(self) -> None:
        command = MotionCommandMessage(
            command_type="step_to_cell",
            target_cell=(2, 3),
            linear_velocity=0.5,
            angular_velocity=0.0,
            stop=False,
            goal_id="goal_motion",
            sequence_id=6,
        )

        self.assertEqual(
            deserialize_message(serialize_message(command), MotionCommandMessage),
            command,
        )

    def test_motor_status_round_trip(self) -> None:
        status = MotorStatusMessage(
            state="applied",
            mode="track_cell",
            applied=True,
            brake=False,
            emergency_stop=False,
            target_cell=(2, 3),
            applied_forward_speed=0.4,
            applied_turn_rate=0.1,
            left_wheel_speed=0.38,
            right_wheel_speed=0.42,
            goal_id="goal_motor",
            sequence_id=7,
            detail="Stub driver applied mode=track_cell.",
        )

        self.assertEqual(
            deserialize_message(serialize_message(status), MotorStatusMessage),
            status,
        )

    def test_mission_state_round_trip(self) -> None:
        state = MissionStateMessage(
            state="navigating",
            detail="Motor layer accepted movement command.",
            goal_id="goal_state",
            planner_state="success",
            navigation_state="following_path",
            motor_mode="track_cell",
            motor_state="applied",
            emergency_stop=False,
        )

        self.assertEqual(
            deserialize_message(serialize_message(state), MissionStateMessage),
            state,
        )


if __name__ == "__main__":
    unittest.main()
