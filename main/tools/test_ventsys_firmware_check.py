import unittest
from ventsys_firmware_check import compare

class FirmwareCheckTests(unittest.TestCase):
    def setUp(self): self.good = {"mac":"aa:bb:cc:dd:ee:ff", "position":60, "open":60, "closed":30, "pwm_active":False, "accepted_image":True}
    def test_same_state_passes(self): self.assertEqual(compare(self.good, dict(self.good)), [])
    def test_changed_position_and_identity_fail(self): self.assertEqual(len(compare(self.good, self.good | {"mac":"00:00:00:00:00:01", "position":30})), 2)
    def test_unknown_pwm_and_unaccepted_image_are_indeterminate(self):
        for update in ({"pwm_active":None}, {"pwm_active":True}, {"accepted_image":False}, {"position":float("nan")}, {"closed":60}):
            with self.assertRaises(ValueError): compare(self.good, self.good | update)

if __name__ == "__main__": unittest.main()
