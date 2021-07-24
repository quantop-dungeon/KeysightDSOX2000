import unittest
import matplotlib.pyplot as plt

from keysightdsox2000 import DSOX2000


class InstrTest(unittest.TestCase):
    def __init__(self, address=''):
        self.instr_address = address

    def test_init(self):
        s = DSOX2000(self.instr_address)
        id = s.comm.query("*IDN?")
        print(f"Instrument IDN string: {id}")

    def test_get_trace(self):
        s = DSOX2000(self.instr_address)

        n = 1  # Channel number

        s.aquire_single()
        tr = s.get_trace(n)
        tr2 = s.get_trace(f"chan{n}")
        s.acquire_continuous()

        self.assertEqual(tr, tr2)
        self.assertEqual(tr["x"].shape, tr["y"].shape)

        plt.plot(tr["x"], tr["y"])
        plt.xlabel('%s (%s)' % (tr['name_x'], tr['unit_x']))
        plt.ylabel('%s (%s)' % (tr['name_y'], tr['unit_y']))

    def test_measure_average_voltage(self):
        s = DSOX2000(self.instr_address)

        n = 1  # Channel number

        s.aquire_single()
        v = s.measure_average_voltage(self, n)
        v2 = s.measure_average_voltage(self, f"chan{n}")
        s.acquire_continuous()

        self.assertEqual(v, v2)

        print(f"Average voltage level on channel {n} = {v} Volts.")


if __name__ == "__main__":
    unittest.main()
