"""Launch Bukid Tycoon:  python main.py"""

import sys


def main():
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is missing. On Ubuntu/Debian run:  sudo apt install python3-tk")
        print("On Windows and macOS, reinstall Python from python.org (Tkinter is included).")
        sys.exit(1)

    from ui import BukidApp

    root = tk.Tk()
    BukidApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
