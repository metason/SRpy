# tests/test.py

import unittest

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result

if __name__ == '__main__':
    run_tests()
