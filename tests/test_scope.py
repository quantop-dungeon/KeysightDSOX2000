import unittest

from dsox2024 import DSOX2024

class ScopeTest(unittest.TestCase):
    def test_init(self):
        s = DSOX2024()

    def test_get_short_trace(self):
        s = DSOX2024()
        
        x, y = s.get_trace(1, 100)

        self.assertEquals(x.shape, y.shape)

if __name__ == "__main__":
    unittest.main()