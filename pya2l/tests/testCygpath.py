import unittest

from pya2l.utils import cygpathToWin


class TestCygpath(unittest.TestCase):
    def test01(self):
        self.assertEqual(
            cygpathToWin("/cygdrive/c/projects/foobar/flonz"),
            r"c:\projects\foobar\flonz",
        )

    def test02(self):
        self.assertEqual(cygpathToWin(r"c:\projects\foobar\flonz"), r"c:\projects\foobar\flonz")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
