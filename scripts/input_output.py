# import functions to read xml file and visualize commonroad objects
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.visualization.mp_renderer import MPRenderer

# generate path of the file to be opened
file_path = "/home/tai/commonroad-dataset-converter/commonroad_dataset_converter/datasets/rounD/maps/superd.xml"

# read in the scenario and planning problem set
scenario, planning_problem_set = CommonRoadFileReader(file_path).open()

# plot the scenario
rnd = MPRenderer(figsize=(25, 10))
scenario.draw(rnd)
rnd.render(show=True)