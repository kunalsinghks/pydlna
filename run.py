import sys
import os
import multiprocessing

# Add the current directory to path so pydlna package is found
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.append(base_path)
os.chdir(base_path) # Ensure CWD is the executable directory

from pydlna.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
