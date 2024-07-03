import tkinter as tk

class GIFPlayer(tk.Tk):
    def __init__(self, gif_file):
        super().__init__()
        self.gif_file = gif_file
        self.gif_photo = tk.PhotoImage(file=self.gif_file)
        self.label = tk.Label(self)
        self.label.pack()
        self.frame_index = 0
        self.play_gif()

    def play_gif(self):
        try:
            # 尝试加载当前帧
            photo = tk.PhotoImage(file=self.gif_file, format=f"gif -index {self.frame_index}")
            self.label.configure(image=photo)
            self.label.image = photo  # 需要保持对photo的引用
            self.frame_index += 1
        except tk.TclError:
            # 如果帧索引超出范围，从头开始
            self.frame_index = 0
            photo = tk.PhotoImage(file=self.gif_file, format=f"gif -index {self.frame_index}")
            self.label.configure(image=photo)
            self.label.image = photo
            self.frame_index += 1
        # 设置定时器，继续播放下一帧
        self.after(100, self.play_gif)  # 100毫秒后调用self.play_gif

if __name__ == "__main__":
    app = GIFPlayer("picture/emotion/默认.gif")  # 替换为你的GIF文件路径
    app.mainloop()