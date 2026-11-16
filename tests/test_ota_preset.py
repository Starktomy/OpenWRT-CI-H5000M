# SPDX-License-Identifier: MIT
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'Scripts/OnlineUpgradePreset.sh'

class OtaPresetTests(unittest.TestCase):
    def run_preset(self, directory, variant, owner, branch):
        env = {**os.environ, 'WRT_CONFIG': 'H5000M-' + variant, 'WRT_INFO': owner,
               'WRT_BRANCH': branch, 'WRT_DATE': '26.11.16-20.00.00'}
        return subprocess.run(['bash', str(SCRIPT)], cwd=directory, env=env, capture_output=True, text=True)

    def test_all_profiles_embed_real_identity_and_default_to_clean(self):
        closed = 'SOURCE_REPO:-Starktomy/CloseWRT-CI-H5000M}' in SCRIPT.read_text()
        owner, branch, driver = ('chasey-dev', '25.12-dev-wifi7', 'mt_wifi7') if closed else ('immortalwrt', 'master', 'mt76')
        for variant in ('qmodem-next', 'qmodem', 'modem-pro', 'mt5700', 'mt5700m'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                result = self.run_preset(directory, variant, owner, branch)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                path = Path(directory) / 'files/usr/share/h5000m/firmware.json'
                identity = json.loads(path.read_text())
                self.assertEqual((identity['driver'], identity['variant']), (driver, variant))
                self.assertEqual(identity['device'], 'hiveton,h5000m')
                config = (Path(directory) / 'files/etc/config/online-upgrade').read_text()
                self.assertIn("option keep_config '0'", config)
                self.assertIn("option plugin_repo 'Starktomy/H5000M-OTA'", config)

    def test_unknown_source_fails_instead_of_inventing_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_preset(directory, 'qmodem-next', 'unknown', 'unknown')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(directory) / 'files/usr/share/h5000m/firmware.json').exists())

if __name__ == '__main__':
    unittest.main()
