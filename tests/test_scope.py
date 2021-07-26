import unittest
import matplotlib.pyplot as plt

from time import sleep

from keysightdsox2000 import DSOX2000


class InstrTest(unittest.TestCase):
    instr_address = 'TCPIP0::a-dx2024a-41999::5025::SOCKET'

    def test_init(self):
        s = DSOX2000(self.instr_address)
        id = s.comm.query("*IDN?")
        print(f"Instrument IDN string: {id}\n")

    def test_get_trace(self):
        s = DSOX2000(self.instr_address)

        n = 1  # Channel number

        s.aquire_single()
        
        # The wait interval is needed for the two traces read below to be equal. 
        sleep(1)

        tr = s.get_trace(n)
        print("Successfully read a trace usng an integer channel number.")
        tr2 = s.get_trace(f"chan{n}")
        print("Successfully read a trace using a string channel name.")
        s.acquire_continuous()

        self.assertTrue((tr["x"] == tr2["x"]).all())
        self.assertTrue((tr["y"] == tr2["y"]).all())
        self.assertEqual(tr["x"].shape, tr["y"].shape)

        plt.plot(tr["x"], tr["y"])
        plt.xlabel('%s (%s)' % (tr['name_x'], tr['unit_x']))
        plt.ylabel('%s (%s)' % (tr['name_y'], tr['unit_y']))

    def test_measure_average_voltage(self):
        s = DSOX2000(self.instr_address)

        n = 1  # Channel number

        s.aquire_single()
        v = s.measure_average_voltage(n)
        v2 = s.measure_average_voltage(f"chan{n}")
        s.acquire_continuous()

        self.assertEqual(v, v2)

        print(f"Average voltage level on channel {n} = {v} Volts.")


if __name__ == "__main__":
    unittest.main()
