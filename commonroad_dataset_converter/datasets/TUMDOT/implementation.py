import json
import pandas as pd
from pathlib import Path
from commonroad.common.file_writer import CommonRoadFileWriter, FileFormat, OverwriteExistingFile
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.geometry.shape import Circle, Rectangle
from commonroad.prediction.prediction import TrajectoryPrediction
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.scenario import Scenario, ScenarioID, Location, Tag
from commonroad.scenario.state import CustomState, InitialState
from commonroad.scenario.trajectory import Trajectory
from commonroad.planning.planning_problem import PlanningProblemSet

from commonroad_dataset_converter.conversion.tabular.job_consumer import _create_obstacle

# Define a mapping from integer to ObstacleType
INTEGER_TO_OBSTACLE_TYPE = {
    0: ObstacleType.UNKNOWN,
    1: ObstacleType.CAR,
    2: ObstacleType.TRUCK,
    3: ObstacleType.BUS,
    4: ObstacleType.BICYCLE,
    5: ObstacleType.PEDESTRIAN,
    6: ObstacleType.PRIORITY_VEHICLE,
    7: ObstacleType.PARKED_VEHICLE,
    8: ObstacleType.CONSTRUCTION_ZONE,
    9: ObstacleType.TRAIN,
    10: ObstacleType.ROAD_BOUNDARY,
    11: ObstacleType.MOTORCYCLE,
    12: ObstacleType.TAXI,
    13: ObstacleType.BUILDING,
    14: ObstacleType.PILLAR,
    15: ObstacleType.MEDIAN_STRIP
}

# Load CSV data
def load_csv_data(file_path):
    return pd.read_csv(file_path)

# Helper function to create dynamic obstacles using the _create_obstacle method
def create_dynamic_obstacles(csv_data):
    obstacles = []
    for idx, (i, row) in enumerate(csv_data.iterrows(), start=1):
        obstacle_type = INTEGER_TO_OBSTACLE_TYPE.get(row['category'], ObstacleType.UNKNOWN)
        dynamic_obstacle_id = idx
        track_meta = pd.Series({
            'obstacle_type': obstacle_type,
            'length': row['dimension_x'],
            'width': row['dimension_y']
        })
        timestamp = int(row["timestamp"])
        timestamp = max(0, timestamp)
        track_df = pd.DataFrame({
            'time_step': [timestamp],
            'x': [row['translation_x']],
            'y': [row['translation_y']],
            'orientation': [row['rotation_z']],
            'velocity': [row['velocity_x']],
            'acceleration': [row['acceleration_x']]
        })

        obstacle = _create_obstacle(track_df, track_meta, dynamic_obstacle_id)
        obstacles.append(obstacle)


    return obstacles

def main():

    csv_data_path = '/home/valery/PycharmProjects/commonroad-dataset-converter5/tests/resources/TUMDOT-MUC/Trajectory Data/test_csv'
    input_xml_path = '/home/valery/PycharmProjects/commonroad-dataset-converter5/commonroad_dataset_converter/datasets/TUMDOT/output_file6.xml'
    output_xml_path = '/home/valery/PycharmProjects/commonroad-dataset-converter5/commonroad_dataset_converter/datasets/TUMDOT/output_file8.xml'

    csv_data = load_csv_data(csv_data_path)

    # Read the existing scenario
    reader = CommonRoadFileReader(input_xml_path)
    scenario, planning_problem_set = reader.open()

    # Add dynamic obstacles to the scenario
    obstacles = create_dynamic_obstacles(csv_data)
    for obstacle in obstacles:
        scenario.add_objects(obstacle)

    # Save the updated scenario
    writer = CommonRoadFileWriter(
        scenario=scenario,
        planning_problem_set=planning_problem_set,
        author="Sebastian Maierhofer",
        affiliation="Technical University of Munich",
        source="CommonRoad Scenario Designer",
        tags={Tag.URBAN},
    )
    writer.write_to_file(output_xml_path, OverwriteExistingFile.ALWAYS)

    print(f"Scenario saved to: {output_xml_path}")

if __name__ == "__main__":
    main()
