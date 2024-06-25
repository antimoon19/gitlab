import unittest
from pathlib import Path
from factory import AutomatumConverterFactory

class TestAutomatumConversion(unittest.TestCase):
    def setUp(self):
        self.input_dir = Path(".")
        self.output_dir = Path("output")
        self.map_file = Path("DEU_appershofen-1.xml")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        dynamic_world_file = self.input_dir / "dynamicWorld.json"
        if not dynamic_world_file.exists():
            raise FileNotFoundError(f"{dynamic_world_file} not found in current directory.")

        if not self.map_file.exists():
            raise FileNotFoundError(f"{self.map_file} not found in current directory.")

    def test_read_dynamic_world(self):
        factory = AutomatumConverterFactory(
            input_dir=self.input_dir, output_dir=self.output_dir, map_file=self.map_file
        )
        recording_generator = factory.build_recording_generator()
        job_processor = factory.build_job_processor()

        for traj_df, traj_meta, recording in recording_generator:
            job_processor(traj_df, traj_meta, recording)
            scenario_path = self.output_dir / f"{recording.recording_id}.xml"
            self.assertTrue(scenario_path.exists())
            with scenario_path.open() as f:
                content = f.read()
                self.assertIn('<commonRoad', content)
                self.assertIn('<dynamicObstacle', content)

if __name__ == '__main__':
    unittest.main()
