import unittest


class MyTestCase(unittest.TestCase):
    def test_format(self):
        from formatter.markdown import format
        content = format("")
        print(content)


if __name__ == '__main__':
    unittest.main()
