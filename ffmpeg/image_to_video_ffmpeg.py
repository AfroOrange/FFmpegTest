import tkinter as tk
from tkinter import Label, Button, filedialog
import imageio
from PIL import Image, ImageTk
import ffmpeg

class VideoPlayer:
    def __init__(self, video_path):
        self.root = tk.Tk()
        self.root.title("Looping Video Player")
        self.video_path = video_path
        self.label = Label(self.root)
        self.label.pack()
        self.button = Button(self.root, text="Add Image", command=self.add_image)
        self.button.pack()
        self.video = imageio.get_reader(video_path)
        self.overlay_image_path = None
        self.root.bind("<KeyPress-q>", self.stop_video)  # Bind 'q' key to stop_video method
        self.root.after(0, self.play_video)  # Start playing video after the main loop starts
        self.root.mainloop()

    def play_video(self):
        while True:
            for frame in self.video.iter_data():
                image = Image.fromarray(frame)
                if self.overlay_image_path:
                    image = self.overlay_image_ffmpeg(image)
                photo = ImageTk.PhotoImage(image)
                self.label.config(image=photo)
                self.label.image = photo
                self.root.update()
                self.root.after(30)  # Adjust the delay as needed

    def overlay_image_ffmpeg(self, image):
        input_stream = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{image.width}x{image.height}')
        overlay_stream = ffmpeg.input(self.overlay_image_path)
        output_stream = ffmpeg.output(input_stream, overlay_stream, 'pipe:', format='rawvideo', pix_fmt='rgb24', vframes=1)
        out, _ = ffmpeg.run(output_stream, input=image.tobytes(), capture_stdout=True, capture_stderr=True)
        return Image.frombytes('RGB', (image.width, image.height), out)

    def stop_video(self, event=None):
        # if the user presses q, close the window and stop the video
        self.root.destroy()

    def add_image(self):
        image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if image_path:
            self.overlay_image_path = image_path
            print(f"Image {image_path} will be overlayed onto the video.")