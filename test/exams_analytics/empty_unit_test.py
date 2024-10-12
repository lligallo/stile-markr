import unittest

class EmptyUnitTest(unittest.IsolatedAsyncioTestCase):

    async def test_always_true(self):
        print("Just an always true tests")
        self.assertTrue(True)

print("Just an empty unit test")
if __name__ == '__main__':
    unittest.main()