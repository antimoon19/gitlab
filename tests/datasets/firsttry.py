import os
import uuid
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.common.file_writer import CommonRoadFileWriter
from opendrive2lanelet.opendriveparser import parse_opendrive
from opendrive2lanelet.converter import convert_opendrive
from commonroad.scenario.traffic_sign import TrafficSign
from commonroad.scenario.lanelet import LaneletNetwork
from commonroad.scenario.scenario import Scenario, Tag

# Funktion zur Erstellung von Szenarien aus einer OpenDRIVE-Datei
def create_scenarios_from_xodr(xodr_path, output_dir):
    # OpenDRIVE-Datei lesen und parsen
    with open(xodr_path, 'r') as f:
        xodr_content = f.read()

    opendrive_map = parse_opendrive(xodr_content)

    # Konvertiere OpenDRIVE zu Lanelet
    lanelet_map, traffic_rules = convert_opendrive(opendrive_map)

    # Erzeuge ein CommonRoad-Szenario aus dem Lanelet-Map
    lanelet_network = LaneletNetwork.create_from_lanelet_map(lanelet_map)

    # Beispielhaftes Szenario erstellen (kann erweitert werden, um mehrere Szenarien zu generieren)
    scenario = Scenario(100, 0, lanelet_network=lanelet_network)
    scenario.tags.append(Tag('converted from XODR'))

    # Erzeuge einen eindeutigen Dateinamen für das Szenario
    scenario_id = uuid.uuid4()
    commonroad_output_path = os.path.join(output_dir, f'scenario_{scenario_id}.xml')

    # Speichere das CommonRoad-Szenario in eine XML-Datei
    writer = CommonRoadFileWriter(scenario)
    writer.write_to_file(commonroad_output_path)

    print(f"Das Szenario wurde erfolgreich konvertiert und unter {commonroad_output_path} gespeichert.")

# Pfad zur XODR-Datei und zum Ausgabe-Verzeichnis
xodr_path = 'path/to/your/file.xodr'
output_dir = 'path/to/your/output_directory'

# Erstelle das Ausgabe-Verzeichnis, falls es nicht existiert
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Szenarien erstellen
create_scenarios_from_xodr(xodr_path, output_dir)
