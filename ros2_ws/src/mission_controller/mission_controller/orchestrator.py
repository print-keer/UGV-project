from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from autonomy_interfaces.contracts import (
    MissionGoalMessage,
    PLANNER_NO_PATH,
    NavigationStatusMessage,
    OccupancyGridMessage,
    PlannedPathMessage,
    PlannerStatusMessage,
    ReplanRequestMessage,
)
from mapping.dynamic_world import DynamicWorld
from mapping.mock_maps import MockMap
from mapping.map_provider import MapProvider
from navigation.path_follower import NavigationReport, PathFollower
from path_planner.planning_pipeline import PlanningPipeline
from .topic_bus import TopicBus
from .topics import (
    MISSION_GOAL_TOPIC,
    NAVIGATION_STATUS_TOPIC,
    OCCUPANCY_GRID_TOPIC,
    PLANNED_PATH_TOPIC,
    PLANNER_STATUS_TOPIC,
    REPLAN_REQUEST_TOPIC,
)


@dataclass(frozen=True)
class MissionExecution:
    occupancy_grid: OccupancyGridMessage
    mission_goal: MissionGoalMessage
    planned_path: PlannedPathMessage
    planner_status: PlannerStatusMessage
    navigation_status: NavigationStatusMessage
    replan_request: Optional[ReplanRequestMessage]
    navigation_report: NavigationReport


@dataclass(frozen=True)
class TopicMissionExecution:
    initial_execution: MissionExecution
    final_execution: MissionExecution
    published_topics: list[str]
    replanned: bool


@dataclass(frozen=True)
class DynamicMissionStep:
    occupancy_revision: int
    planner_state: str
    navigation_state: str
    path_found: bool
    path: list[tuple[int, int]]
    applied_obstacle: tuple[int, int] | None = None
    recovery_action: str | None = None


@dataclass(frozen=True)
class DynamicMissionExecution:
    map_name: str
    steps: list[DynamicMissionStep]
    total_replans: int
    terminal_state: str


class MissionOrchestrator:
    """Simulation-first controller for Person 1 node boundaries."""

    def __init__(
        self,
        planning_pipeline: PlanningPipeline | None = None,
        path_follower: PathFollower | None = None,
        map_provider: MapProvider | None = None,
    ) -> None:
        self.planning_pipeline = planning_pipeline or PlanningPipeline()
        self.path_follower = path_follower or PathFollower()
        self.map_provider = map_provider or MapProvider()

    def execute(
        self,
        occupancy_grid: OccupancyGridMessage,
        mission_goal: MissionGoalMessage,
    ) -> MissionExecution:
        planned_path, planner_status = self.planning_pipeline.plan_for_goal(
            occupancy_grid,
            mission_goal,
        )
        navigation_report = self.path_follower.consume_path(planned_path)
        return MissionExecution(
            occupancy_grid=occupancy_grid,
            mission_goal=mission_goal,
            planned_path=planned_path,
            planner_status=planner_status,
            navigation_status=navigation_report.status,
            replan_request=navigation_report.replan_request,
            navigation_report=navigation_report,
        )

    def recover_no_path(
        self,
        occupancy_grid: OccupancyGridMessage,
        mission_goal: MissionGoalMessage,
    ) -> MissionExecution:
        fallback_start = mission_goal.start_cell or occupancy_grid.origin
        fallback_goal = MissionGoalMessage(
            start_cell=fallback_start,
            goal_cell=mission_goal.goal_cell,
            goal_id=mission_goal.goal_id,
        )
        return self.execute(occupancy_grid, fallback_goal)

    def execute_with_topics(
        self,
        occupancy_grid: OccupancyGridMessage,
        mission_goal: MissionGoalMessage,
        blocked_cell: tuple[int, int] | None = None,
    ) -> TopicMissionExecution:
        bus = TopicBus()

        latest_grid = occupancy_grid
        latest_goal = mission_goal

        planner_messages: dict[str, object] = {}
        navigation_messages: dict[str, object] = {}

        def on_goal(goal: MissionGoalMessage) -> None:
            planner_messages["goal"] = goal

        def on_grid(grid: OccupancyGridMessage) -> None:
            planner_messages["grid"] = grid

        def on_path(path: PlannedPathMessage) -> None:
            navigation_messages["path"] = path

        bus.subscribe(MISSION_GOAL_TOPIC, on_goal)
        bus.subscribe(OCCUPANCY_GRID_TOPIC, on_grid)
        bus.subscribe(PLANNED_PATH_TOPIC, on_path)

        bus.publish(OCCUPANCY_GRID_TOPIC, latest_grid)
        bus.publish(MISSION_GOAL_TOPIC, latest_goal)

        initial_execution = self.execute(latest_grid, latest_goal)
        bus.publish(PLANNER_STATUS_TOPIC, initial_execution.planner_status)
        bus.publish(PLANNED_PATH_TOPIC, initial_execution.planned_path)
        bus.publish(NAVIGATION_STATUS_TOPIC, initial_execution.navigation_status)

        final_execution = initial_execution
        replanned = False

        if blocked_cell and blocked_cell in initial_execution.planned_path.waypoints:
            blocked_report = self.path_follower.detect_blocked_waypoint(
                initial_execution.planned_path,
                blocked_cell,
            )
            bus.publish(NAVIGATION_STATUS_TOPIC, blocked_report.status)
            if blocked_report.replan_request is not None:
                bus.publish(REPLAN_REQUEST_TOPIC, blocked_report.replan_request)
                latest_grid = self.map_provider.clone_with_obstacle(latest_grid, blocked_cell)
                replanned_goal = MissionGoalMessage(
                    start_cell=blocked_report.status.current_cell
                    or latest_goal.start_cell
                    or latest_grid.origin,
                    goal_cell=latest_goal.goal_cell,
                    goal_id=latest_goal.goal_id,
                )
                bus.publish(OCCUPANCY_GRID_TOPIC, latest_grid)
                bus.publish(MISSION_GOAL_TOPIC, replanned_goal)
                final_execution = self.execute(latest_grid, replanned_goal)
                bus.publish(PLANNER_STATUS_TOPIC, final_execution.planner_status)
                bus.publish(PLANNED_PATH_TOPIC, final_execution.planned_path)
                bus.publish(NAVIGATION_STATUS_TOPIC, final_execution.navigation_status)
                replanned = True

        return TopicMissionExecution(
            initial_execution=initial_execution,
            final_execution=final_execution,
            published_topics=[entry.topic for entry in bus.published_messages],
            replanned=replanned,
        )

    def execute_dynamic_world(
        self,
        mock_map: MockMap,
    ) -> DynamicMissionExecution:
        world = DynamicWorld(mock_map, self.map_provider)
        mission_goal = MissionGoalMessage(
            start_cell=mock_map.start,
            goal_cell=mock_map.goal,
            goal_id=mock_map.name,
        )
        steps: list[DynamicMissionStep] = []

        initial_execution = self.execute(world.current_grid, mission_goal)
        steps.append(
            DynamicMissionStep(
                occupancy_revision=initial_execution.occupancy_grid.revision,
                planner_state=initial_execution.planner_status.state,
                navigation_state=initial_execution.navigation_status.state,
                path_found=initial_execution.planned_path.path_found,
                path=initial_execution.planned_path.waypoints,
            )
        )

        total_replans = 0
        while world.remaining_updates > 0:
            world_step = world.advance()
            current_execution = self.execute(world_step.occupancy_grid, mission_goal)
            recovery_action: str | None = None
            if current_execution.planner_status.state == PLANNER_NO_PATH:
                recovery_action = "hold_position_and_report_no_path"
            steps.append(
                DynamicMissionStep(
                    occupancy_revision=current_execution.occupancy_grid.revision,
                    planner_state=current_execution.planner_status.state,
                    navigation_state=current_execution.navigation_status.state,
                    path_found=current_execution.planned_path.path_found,
                    path=current_execution.planned_path.waypoints,
                    applied_obstacle=world_step.applied_obstacle,
                    recovery_action=recovery_action,
                )
            )
            total_replans += 1

        return DynamicMissionExecution(
            map_name=mock_map.name,
            steps=steps,
            total_replans=total_replans,
            terminal_state=steps[-1].planner_state,
        )
