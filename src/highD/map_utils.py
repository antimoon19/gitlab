import numpy as np
from typing import Union, List
from pandas import DataFrame
from enum import Enum

from commonroad.scenario.scenario import Scenario
from commonroad.scenario.lanelet import Lanelet, LaneletType, RoadUser, LineMarking
from commonroad.scenario.traffic_sign import TrafficSignIDGermany, TrafficSignElement, TrafficSign


class Direction(Enum):
    """
    Enum for representing upper or lower interstate road
    """
    UPPER = 1
    LOWER = 2


def get_lane_markings(recording_df: DataFrame):
    """
    Extracts upper and lower lane markings from data frame

    :param recording_df: data frame of the recording meta information
    :return: speed limit
    """
    upper_lane_markings = [-float(x) for x in recording_df.upperLaneMarkings.values[0].split(";")]
    lower_lane_markings = [-float(x) for x in recording_df.lowerLaneMarkings.values[0].split(";")]
    return upper_lane_markings, lower_lane_markings


def get_dt(recording_df: DataFrame) -> float:
    """
    Extracts time step size from data frame

    :param recording_df: data frame of the recording meta information
    :return: time step size
    """
    return 1./recording_df.frameRate.values[0]


def get_speed_limit(recording_df: DataFrame) -> Union[float, None]:
    """
    Extracts speed limit from data frame

    :param recording_df: data frame of the recording meta information
    :return: speed limit
    """
    speed_limit = recording_df.speedLimit.values[0]
    if speed_limit < 0:
        return None
    else:
        return speed_limit


def get_meta_scenario(dt: float, benchmark_id: str, lane_markings: List[float], speed_limit: float,
                      road_length: int, direction: Direction, road_offset: int):
    """
    Generates meta CommonRoad scenario containing only lanelet network

    :param dt: time step size
    :param benchmark_id: benchmark ID of meta scenario
    :param lane_markings: list of y-positions for lane markings
    :param speed_limit: speed limits for road
    :param road_length: length of road
    :param direction: indicator for upper or lower interstate road
    :param road_offset: length added on both sides of road
    :return: CommonRoad scenario
    """
    scenario = Scenario(dt, benchmark_id)
    for i in range(len(lane_markings) - 1):
        # get two lines of current lane
        lane_y = lane_markings[i]
        next_lane_y = lane_markings[i + 1]
        x_vec = np.linspace(-road_offset, road_length + road_offset, num=road_length + 2 * road_offset)
        lane_y_vec = np.ones(road_length + 2 * road_offset) * lane_y
        next_lane_y_vec = np.ones(road_length + 2 * road_offset) * next_lane_y

        if direction is Direction.UPPER:
            x_vec = np.flip(x_vec)

        left_vertices = np.squeeze(np.dstack((x_vec, lane_y_vec)))
        right_vertices = np.squeeze(np.dstack((x_vec, next_lane_y_vec)))
        center_vertices = (left_vertices + right_vertices) / 2.0

        # assign lanelet ID and adjacent IDs and lanelet types
        lanelet_id = i + 1
        lanelet_type = {LaneletType.INTERSTATE, LaneletType.MAIN_CARRIAGE_WAY}
        if direction is Direction.LOWER:
            if lanelet_id == 0:
                adjacent_left = lanelet_id + 1
                adjacent_left_same_direction = True
                adjacent_right = None
                adjacent_right_same_direction = False
                line_marking_left_vertices = LineMarking.DASHED
                line_marking_right_vertices = LineMarking.SOLID
            elif lanelet_id == len(lane_markings) - 1:
                adjacent_right = lanelet_id - 1
                adjacent_right_same_direction = True
                adjacent_left = None
                adjacent_left_same_direction = False
                line_marking_left_vertices = LineMarking.SOLID
                line_marking_right_vertices = LineMarking.DASHED
            else:
                adjacent_right = lanelet_id - 1
                adjacent_right_same_direction = True
                adjacent_left = lanelet_id + 1
                adjacent_left_same_direction = True
                line_marking_left_vertices = LineMarking.DASHED
                line_marking_right_vertices = LineMarking.DASHED
        else:
            if lanelet_id == len(lane_markings) - 1:
                adjacent_left = lanelet_id - 1
                adjacent_left_same_direction = True
                adjacent_right = None
                adjacent_right_same_direction = False
                line_marking_left_vertices = LineMarking.DASHED
                line_marking_right_vertices = LineMarking.SOLID
            elif lanelet_id == 0:
                adjacent_right = lanelet_id + 1
                adjacent_right_same_direction = True
                adjacent_left = None
                adjacent_left_same_direction = False
                line_marking_left_vertices = LineMarking.SOLID
                line_marking_right_vertices = LineMarking.DASHED
            else:
                adjacent_right = lanelet_id + 1
                adjacent_right_same_direction = True
                adjacent_left = lanelet_id - 1
                adjacent_left_same_direction = True
                line_marking_left_vertices = LineMarking.DASHED
                line_marking_right_vertices = LineMarking.DASHED

        # add lanelet to scenario
        scenario.add_objects(
            Lanelet(lanelet_id=lanelet_id, left_vertices=left_vertices,  right_vertices=right_vertices,
                    center_vertices=center_vertices, adjacent_left=adjacent_left,
                    adjacent_left_same_direction=adjacent_left_same_direction, adjacent_right=adjacent_right,
                    adjacent_right_same_direction=adjacent_right_same_direction, user_one_way={RoadUser.VEHICLE},
                    line_marking_left_vertices=line_marking_left_vertices,
                    line_marking_right_vertices=line_marking_right_vertices, lanelet_type=lanelet_type))

    # store speed limit for traffic sign generation
    if speed_limit is not None:
        traffic_sign_element = TrafficSignElement(TrafficSignIDGermany.MAX_SPEED, [str(speed_limit)])
        position = scenario.lanelet_network.lanelets[0].right_vertices[0]
        lanelets = {lanelet.lanelet_id for lanelet in scenario.lanelet_network.lanelets}
        traffic_sign = TrafficSign(scenario.generate_object_id(), [traffic_sign_element], lanelets, position)

        scenario.add_objects(traffic_sign, lanelets)

    return scenario
