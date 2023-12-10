import unittest

from constants import Actions, ACTION_IDX_TO_ACTION_MAP
from environment import Environment


class TestEnvironment(unittest.TestCase):
    
    def test_get_solar_gain_time_bounds(self):
        sim = Environment()
        self.assertIsInstance(sim.get_solar_gain(0), float)
        with self.assertRaises(AssertionError): 
            sim.get_solar_gain(-1)
        with self.assertRaises(AssertionError): 
            sim.get_solar_gain(1441)

    def test_get_solar_gain_values(self):
        sim = Environment(intensity_multiplier=1)
        self.assertAlmostEqual(sim.get_solar_gain(0), 0.0)
        self.assertGreater(sim.get_solar_gain(720), 0.5)
        self.assertAlmostEqual(sim.get_solar_gain(1400), 0.0)

    def test_get_reward_negative_power_should_be_negative(self):
        sim = Environment()
        for action in ACTION_IDX_TO_ACTION_MAP:
            self.assertLessEqual(sim.get_reward(action, -50, 0), 0)

    def test_get_reward_sending_should_be_positive(self):
        sim = Environment()
        self.assertGreaterEqual(sim.get_reward(Actions.SEND, 1, 1), 0)

    def test_get_reward_sending_should_be_positive(self):
        sim = Environment()
        self.assertGreaterEqual(sim.get_reward(Actions.COLLECT, 1, 1), 0)

    def test_get_reward_sleep_should_be_negative(self):
        sim = Environment()
        self.assertLessEqual(sim.get_reward(Actions.SLEEP, 1, 1), 0)
        
