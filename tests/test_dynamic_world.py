from __future__ import annotations

import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / "ros2_ws" / "src"
for package_dir in src_root.iterdir():
    if package_dir.is_dir():
        sys.path.insert(0, str(package_dir))

from mapping.dynamic_world import DynamicWorld
from mapping.mock_maps import MockMap
from autonomy_interfaces.contracts import SensorObservationMessage
from mapping.sensor_fusion import SensorFusionEngine


class DynamicWorldTests(unittest.TestCase):
    def test_dynamic_world_advances_obstacle_sequence(self) -> None:
        mock_map = MockMap(
            name="dynamic_sequence",
            description="Sequence test map.",
            start=(0, 0),
            goal=(1, 3),
            grid=[
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            dynamic_obstacles=[(0, 1), (1, 2)],
        )

        world = DynamicWorld(mock_map)
        timeline = world.full_timeline()

        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0].occupancy_grid.revision, 0)
        self.assertEqual(timeline[1].applied_obstacle, (0, 1))
        self.assertEqual(timeline[2].applied_obstacle, (1, 2))
        self.assertTrue(timeline[-1].scenario_complete)

    def test_dynamic_world_sensor_step_updates_grid(self) -> None:
        mock_map = MockMap(
            name="sensor_sequence",
            description="Sensor-driven update test.",
            start=(0, 0),
            goal=(1, 2),
            grid=[
                [0, 0, 0],
                [0, 0, 0],
            ],
            lidar_observations=[[(0, 1)]],
            ultrasonic_observations=[[(1, 2)]],
        )

        world = DynamicWorld(mock_map)
        step = world.advance_sensor_step()

        self.assertEqual(step.occupancy_grid.cell_value(0, 1), 1)
        self.assertEqual(step.occupancy_grid.cell_value(1, 2), 1)
        self.assertEqual(len(step.sensor_observations), 2)

    def test_external_sensor_observation_updates_current_grid(self) -> None:
        mock_map = MockMap(
            name="external_sensor",
            description="External observation test.",
            start=(0, 0),
            goal=(1, 2),
            grid=[
                [0, 0, 0],
                [0, 0, 0],
            ],
        )

        world = DynamicWorld(mock_map)
        step = world.apply_external_observation(
            SensorObservationMessage(
                sensor_type="lidar",
                detected_cells=[(1, 1)],
                source_map="external_sensor",
                sequence_id=7,
            )
        )

        self.assertEqual(step.occupancy_grid.cell_value(1, 1), 1)
        self.assertEqual(world.current_grid.cell_value(1, 1), 1)

    def test_sensor_fusion_ignores_out_of_bounds_cells(self) -> None:
        mock_map = MockMap(
            name="bounds",
            description="Bounds filtering test.",
            start=(0, 0),
            goal=(1, 1),
            grid=[
                [0, 0],
                [0, 0],
            ],
        )

        world = DynamicWorld(mock_map)
        updated_grid = SensorFusionEngine().apply_observation(
            world.current_grid,
            SensorObservationMessage(
                sensor_type="lidar",
                detected_cells=[(5, 5), (1, 1)],
                source_map="bounds",
                sequence_id=1,
            ),
        )

        self.assertEqual(updated_grid.cell_value(1, 1), 1)
        self.assertEqual(updated_grid.revision, 1)


if __name__ == "__main__":
    unittest.main()
