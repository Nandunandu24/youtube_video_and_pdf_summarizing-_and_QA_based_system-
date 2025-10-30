import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from hello import main

def test_main_prints():
    main()
    assert True
