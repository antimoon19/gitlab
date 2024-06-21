# General Imports
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from commonroad.scenario.scenario import Tag
from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile
from commonroad.planning.planning_problem import PlanningProblemSet
from crdesigner.common.config import gui_config
from crdesigner.common.config.general_config import general_config
from crdesigner.common.config.opendrive_config import open_drive_config
from commonroad.visualization.mp_renderer import MPRenderer
from crdesigner.map_conversion.map_conversion_interface import opendrive_to_commonroad, lanelet_to_commonroad

input_path = Path('/home/valery/PycharmProjects/commonroad-dataset-converter5/commonroad_dataset_converter/datasets/TUMDOT/Maps/2023-03-22_1477_TEMPUS_Rheinstrasse.xodr')  # replace empty string
save_scenario = True

# specify the coordinate system for Opendrive conversion
open_drive_config.proj_string_odr = gui_config.utm_default # define gerreference according to the .xodr file

scenario = opendrive_to_commonroad(input_path, general_conf=general_config, odr_conf=open_drive_config)
# translate the dataset by x_offset and y_offset from the file within TUMDOT dataset
# Trajectory Data/meta_information.json
scenario.translate_rotate(np.array([-692009.0, -5338095.0]), 0)
# visualize the map
plt.figure()
rnd = MPRenderer(figsize=(10,10))
rnd.draw_params.dynamic_obstacle.draw_icon=True
scenario.draw(rnd)
rnd.draw_params.time_begin = 0
scenario.draw(rnd)
rnd.render()
plt.show()

if save_scenario:
    # store converted file as CommonRoad scenario
    writer = CommonRoadFileWriter(
        scenario=scenario,
        planning_problem_set=PlanningProblemSet(),
        author="Sebastian Maierhofer",
        affiliation="Technical University of Munich",
        source="CommonRoad Scenario Designer",
        tags={Tag.URBAN},
    )
    writer.write_to_file(os.path.dirname(os.path.realpath(__file__)) + "/" + "output-file9.xml",
                         OverwriteExistingFile.ALWAYS)