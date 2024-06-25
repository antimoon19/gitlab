from pathlib import Path
import hashlib
from commonroad.common.file_writer import FileFormat, CommonRoadFileWriter
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.trajectory import Trajectory
from commonroad.prediction.prediction import TrajectoryPrediction
from commonroad.scenario.state import InitialState
from commonroad.geometry.shape import Rectangle
from commonroad.planning.planning_problem import PlanningProblemSet
from implementation import AutomatumRecordingGenerator, AutomatumMetaScenarioGenerator

class AutomatumConverterFactory:
    def __init__(self, input_dir: Path, output_dir: Path, map_file: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.map_file = map_file

    def build_recording_generator(self):
        return AutomatumRecordingGenerator(data_path=self.input_dir)

    def build_meta_scenario_creator(self):
        return AutomatumMetaScenarioGenerator(map_file=self.map_file)

    def build_job_processor(self):
        def job_processor(traj_df, traj_meta, recording):
            scenario = self.build_meta_scenario_creator()(traj_df, recording)

            for obstacle_id, obstacle_meta in traj_df.groupby('obstacle_id'):
                obstacle_info = traj_meta.loc[obstacle_id]
                length = obstacle_info['length']
                width = obstacle_info['width']

                states = [
                    InitialState(position=[row.x, row.y], orientation=0, time_step=row.time_step)
                    for row in obstacle_meta.itertuples()
                ]
                trajectory = Trajectory(initial_time_step=states[0].time_step, state_list=states)
                prediction = TrajectoryPrediction(trajectory=trajectory, shape=Rectangle(length=length, width=width))

                obstacle_id_int = int(hashlib.md5(obstacle_id.encode()).hexdigest(), 16) % (10 ** 8)

                obstacle = DynamicObstacle(
                    obstacle_id=obstacle_id_int,
                    obstacle_type=ObstacleType.CAR if obstacle_info['obstacle_type'] == 'CAR' else ObstacleType.TRUCK,
                    initial_state=states[0],
                    prediction=prediction,
                    obstacle_shape=Rectangle(length=length, width=width)
                )
                scenario.add_objects(obstacle)

            scenario_path = self.output_dir / f"{recording.recording_id}.xml"
            scenario_path.parent.mkdir(parents=True, exist_ok=True)
            writer = CommonRoadFileWriter(scenario, PlanningProblemSet(), None)
            writer.write_to_file(scenario_path, FileFormat.XML)
        return job_processor
