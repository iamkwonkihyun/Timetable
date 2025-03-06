import tkinter as tk
import time

def stop_program():
    root.quit()

root = tk.Tk()
label = tk.Label(root, text="시간표")
label.pack()
exit_button = tk.Button(root, text="종료하기", command=stop_program)
exit_button.pack()
root.mainloop()
