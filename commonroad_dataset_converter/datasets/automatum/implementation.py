import copy
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Tuple
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.scenario.scenario import Scenario, ScenarioID, Tag
from openautomatumdronedata.dataset import droneDataset

@dataclass
class AutomatumRecording:
    location: str
    recording_id: int

@dataclass
class AutomatumMetaScenarioGenerator:
    map_file: Path
    _name_to_map: Dict[str, Scenario] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        scenario = CommonRoadFileReader(str(self.map_file)).open()[0]
        self._name_to_map['current_dir'] = scenario

    def __call__(self, traj_df, recording) -> Scenario:
        if recording.location not in self._name_to_map:
            raise KeyError(f"Location '{recording.location}' not found.")
        meta_scenario = copy.deepcopy(self._name_to_map[recording.location])
        meta_scenario.scenario_id = ScenarioID(
            map_name=recording.location,
            map_id=recording.recording_id
        )
        meta_scenario.tags = {Tag.HIGHWAY}
        return meta_scenario

@dataclass
class AutomatumRecordingGenerator:
    data_path: Path

    def __iter__(self) -> Iterable[Tuple[pd.DataFrame, AutomatumRecording]]:
        recording_id = 1
        dataset = droneDataset(self.data_path)
        dynamic_obstacles = dataset.dynWorld.get_list_of_dynamic_objects()

        vehicle_states = []
        vehicle_meta = []

        for dynObject in dynamic_obstacles:
            for t, (x, y) in enumerate(zip(dynObject.x_vec, dynObject.y_vec)):
                vehicle_states.append({
                    'time_step': t,
                    'x': x,
                    'y': y,
                    'obstacle_id': dynObject.UUID
                })

            vehicle_meta.append({
                'obstacle_id': dynObject.UUID,
                'obstacle_type': 'CAR' if dynObject.type == 'car' else 'TRUCK',
                'length': dynObject.length,
                'width': dynObject.width
            })

        traj_df = pd.DataFrame(vehicle_states)
        traj_meta = pd.DataFrame(vehicle_meta).set_index('obstacle_id')

        yield traj_df, traj_meta, AutomatumRecording('current_dir', recording_id)