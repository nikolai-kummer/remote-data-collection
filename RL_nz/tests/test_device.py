import unittest
from environment.device import Device

class TestDevice(unittest.TestCase):
    def test_get_power_level(self):
        device = Device(power_level=1000.0, power_max=2000.0)
        self.assertEqual(device.calculate_power_percentage(), 50)

    def test_get_power_level_rounded(self):
        device = Device(power_level=1000.0, power_max=2000.0, rounding_factor=10)
        self.assertEqual(device.calculate_rounded_power_level(), 5)

    def test_take_action(self):
        device = Device(power_level=1000.0)
        device.take_action(0)
        self.assertEqual(device.get_power_level_float(), 1000-device._power_idle)

    def test_set_power_level(self):
        device = Device(power_max=100)
        device.set_power_percentage(50.0)
        self.assertEqual(device.calculate_power_percentage(), 50)
        
    def test_add_power(self):
        device = Device(power_level=1000.0)
        device.add_power(100)
        self.assertEqual(device.get_power_level_float(), 1100.0)

if __name__ == '__main__':
    unittest.main()