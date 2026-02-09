import sys
import os
import multiprocessing

# Add the current directory to path so pydlna package is found
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    sys.path.append(sys._MEIPASS)
    # Set CWD to executable directory (where config.json is)
    exe_dir = os.path.dirname(sys.executable)
    os.chdir(exe_dir)
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_path)
    os.chdir(base_path)

try:
    from pydlna.main import main
    if __name__ == "__main__":
        multiprocessing.freeze_support()
        main()
except Exception as e:
    # Error logging as last resort
    print(f"Startup error: {e}")
    try:
        import tkinter.messagebox as mb
        mb.showerror("Startup Error", str(e))
    except:
        pass
