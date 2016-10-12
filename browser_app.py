import time
import os

def test_for_done():
    while True:
        if os.path.isfile('/home/browser/.done'):
            return

        time.sleep(10)

test_for_done()




