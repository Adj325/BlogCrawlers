import unittest


class MyTestCase(unittest.TestCase):
    def test_slugify_invalid_os_filename(self):
        fn = "Yarn 源码 | 分布式资源调度引擎 Yarn 内核源码剖析"
        from utils.text import slugify

        fn_slugified = slugify(fn, True)
        self.assertEqual("Yarn-源码-分布式资源调度引擎-Yarn-内核源码剖析", fn_slugified)


if __name__ == '__main__':
    unittest.main()
