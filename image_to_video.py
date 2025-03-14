import tkinter as tk
from tkinter import Label
import imageio
from PIL import Image, ImageTk

class VideoPlayer:
    def __init__(self, video_path, loop_count):
        self.root = tk.Tk()
        self.root.title("Looping Video Player")
        self.video_path = video_path
        self.loop_count = loop_count
        self.label = Label(self.root)
        self.label.pack()
        self.video = imageio.get_reader(video_path)
        self.root.bind("<KeyPress-q>", self.stop_video)  # Bind 'q' key to stop_video method
        self.play_video()
        self.root.mainloop()

    def play_video(self):
        for _ in range(self.loop_count):
            for frame in self.video.iter_data():
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                self.label.config(image=photo)
                self.label.image = photo
                self.root.update()
                self.root.after(30)  # Adjust the delay as needed

    def stop_video(self, event=None):
        # if the user presses q, close the window and stop the video
        self.root.destroy()