import unittest

from keysightdsox2000 import DSOX2020


class ScopeTest(unittest.TestCase):
    def test_init(self):
        DSOX2020()

    def test_get_short_trace(self):
        s = DSOX2020()

        x, y = s.get_trace(1)

        self.assertEqual(x.shape, y.shape)


if __name__ == "__main__":
    unittest.main()
