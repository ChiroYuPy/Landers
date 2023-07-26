import tkinter as tk

fullscreen = True

root = tk.Tk()
monitor_size = [root.winfo_screenwidth(), root.winfo_screenheight()]

vertical_tile_number = 11
if fullscreen:
    tile_size = 64

if fullscreen:
    screen_width = 1200
    screen_height = vertical_tile_number * tile_size
else:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()