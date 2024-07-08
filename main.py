import os
import tkinter as tk
from threading import Thread
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence

import config
from fasterwhisper import initial_model
from config import load_config, save_config, POSITION
from text_process import text_process

# position ={"background_x": 140, "background_y": 97, "bubble_x": 0, "bubble_y": 0, "text_x": 27, "text_y": 23}


class MainApp(tk.Tk) :
    def __init__(self) :
        super().__init__()
        self.hide_id = None
        self.background_image_path = None
        position = config.POSITION
        print("导入配置position，", position)
        self.text_label_y = position["text_y"]
        self.text_label_x = position["text_x"]
        self.gif_current_frame = None
        self.gif_frames = None
        self.thread_LLM = None
        self.thread_audio = None
        self.emotions, self.image_files = self.get_emotions_and_paths()

        self.title("pandaman熊猫头-5s无操作后自动隐藏边框")
        self.geometry("700x700+50+20")
        self.configure(bg='green')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.attributes("-alpha", 0.1)

        self.wm_attributes('-transparentcolor', self['bg'])
        self.wm_attributes('-topmost', True)
        self.overrideredirect(True)
        self.bind("<Button-1>", self.show_border)

        # Create a frame for the main content
        self.main_frame = tk.Frame(self, bg='green')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Load images and resize them to a maximum of 400x400
        self.background_image, is_gif = self.load_and_resize_image("picture/emotion/嘲讽.png", 400, 400)
        if is_gif :
            self.animate_gif()
        self.bubble_image, is_gif = self.load_and_resize_image("picture/bubble/bubble8.png", 1000, 100)

        # Create labels for images and text
        self.background_label = tk.Label(self.main_frame, image=self.background_image, bg='green')
        # self.background_label.attributes("-alpha", 1)
        self.bubble_label = tk.Label(self.main_frame, image=self.bubble_image,bg="green")
        self.text_label = tk.Label(self.main_frame, text="卧槽，怎么是你!", bg='white', fg='black', font=("Arial", 32))

        # Position the labels
        self.background_label.place(x=position["background_x"], y=position["background_y"])
        self.bubble_label.place(x=position["bubble_x"], y=position["bubble_y"])
        self.text_label.place(x=position["text_x"], y=position["text_y"])

        # Create a frame for settings
        self.settings_frame = tk.Frame(self, bg='gray')
        self.settings_frame.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM)

        # Create sliders for position adjustment
        self.slider1=self.create_slider("Back表情 X", self.settings_frame, self.set_background_x, 0, 800, 0, 0)
        self.slider2=self.create_slider("Back表情 Y", self.settings_frame, self.set_background_y, 0, 600, 2, 0)
        self.slider3=self.create_slider("Bubble聊天框 X", self.settings_frame, self.set_bubble_x, 0, 800, 0, 1)
        self.slider4=self.create_slider("Bubble聊天框 Y", self.settings_frame, self.set_bubble_y, 0, 600, 2, 1)
        self.slider5=self.create_slider("Text X", self.settings_frame, self.set_text_x, 0, 800, 0, 2)
        self.slider6=self.create_slider("Text Y", self.settings_frame, self.set_text_y, 0, 600, 2, 2)
        self.settings_frame.pack_forget()
        # self.after(10000, self.change_background_image)
        # self.after(15000, self.change_bubble_image)

        # 创建一个Checkbutton复选框按钮，用于切换置顶状态
        self.topmost_var = tk.BooleanVar()
        # 默认置顶，与窗口初始化属性一致
        self.topmost_var.set(True)
        self.topmost_checkbox = tk.Checkbutton(self.settings_frame, bg='white', text="始终置顶",
                                               variable=self.topmost_var,
                                               command=self.toggle_topmost,width=8, height=5)


        # self.topmost_checkbox.config(width=60px, height=30px)
        self.topmost_checkbox.grid(row=0, column=3, padx=0, pady=0, rowspan=4, columnspan=2)
        self.bind("<Unmap>", self.minimize_window)


    def show_border(self, event) :
        print("show_border")
        # x = self.winfo_x()
        # y = self.winfo_y()
        # print("show_border之前", x, y)
        # width = self.winfo_width()
        # height = self.winfo_height()
        self.overrideredirect(False)
        # 获取标题栏高度，设置窗口的新位置
        # self.update_idletasks()  # 更新窗口以获取新高度
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        # print("titlebar_height", titlebar_height)

        # 重新设置窗口的位置和大小
        # self.geometry(f"{width}x{height}+{x}+{y - titlebar_height}")
        # self.geometry(geometry)
        # self.attributes("-topmost", True)

        # print("show_border之后", self.winfo_x(), self.winfo_y())

        self.settings_frame.pack(fill=tk.BOTH, expand=False, side=tk.BOTTOM)

        if self.hide_id is not None :
            self.after_cancel(self.hide_id)
        self.hide_id = self.after(8000, lambda : self.hide_border(titlebar_height))
        print("8s后自动隐藏边框")
    def hide_border(self, titlebar_height) :
        # 获取当前窗口的位置和大小
        x = self.winfo_x()
        y = self.winfo_y()
        # print("hide_border之前", x, y)
        width = self.winfo_width()
        height = self.winfo_height()
        # y = y + titlebar_height
        # 设置窗口的overrideredirect属性
        self.overrideredirect(True)
        print("hide_border")

        # 重新设置窗口的位置和大小
        self.geometry(f"{width}x{height}+{x}+{y}")
        # print("hide_border之后",self.winfo_x(), self.winfo_y())

        self.settings_frame.pack_forget()


    def create_slider(self, label_text, parent, callback, from_, to, row, column) :
        label = tk.Label(parent, text=label_text, bg='white')
        label.grid(row=row, column=column, padx=5, pady=5)
        slider = ttk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL, command=callback)
        slider.grid(row=row + 1, column=column, padx=5, pady=5)
        return slider

    def toggle_topmost(self) :
        # 切换窗口置顶属性
        print("toggle_topmost", self.topmost_var.get())
        self.attributes("-topmost", self.topmost_var.get())

    def save_settings(self) :
        print("save_settings", config.POSITION)
        save_config(config.POSITION)
        # Save the settings to a file or database

    def get_emotions_and_paths(self):
        path = "./picture/emotion/"
        img_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        image_files = {}
        emotions = []
        for root, dirs, files in os.walk(path) :
            for file in files :
                # 检查文件扩展名是否在支持的列表中
                if any(file.lower().endswith(ext) for ext in img_extensions) :
                    # 去掉后缀名
                    emotion = os.path.splitext(file)[0]
                    image_files[emotion] = os.path.join(root, file)  # 用于后续根据情绪调用图片
                    emotions.append(file)
        return emotions, image_files

    def set_background_x(self, value) :
        print("Setting background x to", value)
        self.background_label.place_forget()
        self.background_label.place(x=int(float(value)), y=self.background_label.winfo_y())
        config.POSITION["background_x"] = int(float(value))

    def set_background_y(self, value) :
        print("Setting background y to", value)
        self.background_label.place_forget()
        self.background_label.place(x=self.background_label.winfo_x(), y=int(float(value)))
        config.POSITION["background_y"] = int(float(value))

    def set_bubble_x(self, value) :
        print("Setting bubble x to", value)
        self.bubble_label.place_forget()
        self.bubble_label.place(x=int(float(value)), y=self.bubble_label.winfo_y())
        config.POSITION["bubble_x"] = int(float(value))

    def set_bubble_y(self, value) :
        print("Setting bubble y to", value)
        self.bubble_label.place_forget()
        self.bubble_label.place(x=self.bubble_label.winfo_x(), y=int(float(value)))
        config.POSITION["bubble_y"] = int(float(value))

    def set_text_x(self, value) :
        print("Setting text x to", value)
        self.text_label.place_forget()
        self.text_label.place(x=int(float(value)), y=self.text_label.winfo_y())
        self.text_label_x = int(float(value))
        config.POSITION["text_x"] = int(float(value))

    def set_text_y(self, value) :
        print("Setting text y to", value)
        self.text_label.place_forget()
        self.text_label.place(x=self.text_label.winfo_x(), y=int(float(value)))
        self.text_label_y = int(float(value))
        config.POSITION["text_y"] = int(float(value))

    def load_and_resize_image(self, image_path, max_width, max_height) :
        is_gif = image_path.endswith(".gif")
        if is_gif :
            # 特殊处理GIF（考虑到缩放和循环播放）
            gif = Image.open(image_path)
            self.gif_frames = [ImageTk.PhotoImage(frame.copy().resize((max_width, max_height), Image.Resampling.LANCZOS)) for
                               frame in ImageSequence.Iterator(gif)]
            self.gif_current_frame = 0
            return self.gif_frames[0], is_gif
        else :
            # 处理其他类型的图像
            pil_image = Image.open(image_path)

            # Calculate the new size while maintaining the aspect ratio
            width_ratio = max_width / pil_image.width
            height_ratio = max_height / pil_image.height
            ratio = min(width_ratio, height_ratio)

            new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))

            # Resize the image
            resized_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert the PIL image to a Tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(resized_image)
            return tk_image, is_gif

    def animate_gif(self) :

        try :
            frame = self.gif_frames[self.gif_current_frame]
            self.gif_current_frame = (self.gif_current_frame + 1) % len(self.gif_frames)
            self.background_label.config(image=frame)
            self.background_label.image = frame  # 保持对图像的引用
            # 使用self.after计划下一帧的回调，并保存返回的ID
            self.gif_after_id = self.after(100, self.animate_gif)  # 调整延时以适配动画速度
        except Exception as e :
            print(f"Error animating GIF: {e}")


    def change_background_image(self,new_image_path) :
        print("change_background_image", new_image_path)
        if new_image_path != self.background_image_path:
            if new_image_path is  None:
                new_image_path = self.image_files.get("默认")  # 替换为新的背景图像路径
                self.background_image_path = new_image_path
                print("image_path is None, using default")
            try:
                # 停止当前的GIF动画播放（如果有的话）
                if hasattr(self, 'gif_after_id') :
                    self.after_cancel(self.gif_after_id)
                    del self.gif_after_id

                self.background_image, is_gif = self.load_and_resize_image(new_image_path, 400, 400)
                self.background_image_path = new_image_path
                if is_gif :
                    self.animate_gif()  # 如果是GIF，开始新的动画播放

            except Exception as e :  # 明确指定捕获 Exception 类型的异常
                print(f"Error loading image: {e}, using default")
                self.background_image, is_gif = self.load_and_resize_image(self.image_files.get("默认"), 400, 400)
                self.background_image_path = self.image_files.get("默认")
                if is_gif :
                    self.animate_gif()  # 如果是GIF，开始新的动画播放
            self.background_label.config(image=self.background_image)
            self.background_label.image = self.background_image
        else:
            print("image_path is same as before, not changing")



    def change_bubble_image(self, new_image_path) :
        if new_image_path is None:
            self.bubble_image = None
        else:
            try:
                self.bubble_image, is_gif = self.load_and_resize_image(new_image_path, 1000, 100)
            except Exception as e :  # 明确指定捕获 Exception 类型的异常
                print(f"Error loading image: {e}, using default")
                self.bubble_image, is_gif = self.load_and_resize_image("picture/bubble/bubble8.png", 1000, 100)
        self.bubble_label.config(image=self.bubble_image)
        self.bubble_label.image = self.bubble_image  # 保持对图像的引用

    def change_text(self, text) :
        if text is None:
            # self.text_label.config(text="")
            self.text_label.place_forget()
            print("text is None, hiding text")
        else:
            self.text_label.place(x=self.text_label_x, y=self.text_label_y)
            self.text_label.config(text=text)

    def change_content(self, background_image_name, text):
        print("change_content", background_image_name, text)
        if text is None:
            bubble_image_path = None
        else:
            text_length = len(text)
            if text_length > 12:
                bubble_image_path = "picture/bubble/bubble16.png"
                print("text_length > 9")
            elif text_length > 7:
                bubble_image_path = "picture/bubble/bubble12.png"
                print("text_length > 6")
            elif text_length > 5:
                bubble_image_path = "picture/bubble/bubble8.png"
                print("text_length > 4")
            elif text_length > 3:
                bubble_image_path = "picture/bubble/bubble5.png"
            else:
                bubble_image_path = "picture/bubble/bubble3.png"
                print("text_length <4")


        if background_image_name is  None:
            background_image_path = self.image_files.get("默认")
        else :
            background_image_path = self.image_files.get(background_image_name, None)
            if not background_image_path :
                background_image_path = self.image_files.get("默认")

        print("背景图片更改为", background_image_path)

        self.change_background_image(background_image_path)
        self.change_bubble_image(bubble_image_path)
        self.change_text(text)

    def start_audio_listening(self):
        self.thread_audio = Thread(target=initial_model,daemon=True)
        self.thread_audio.start()

    def connect_to_llm(self):
        print("Connecting to LLM...")
        self.thread_LLM = Thread(target=text_process, args=(self.change_content, 5), daemon=True)
        self.thread_LLM.start()

    def on_closing(self):
        self.save_settings()
        self.destroy()

    def minimize_window(self, event) :
        print("隐藏或者取消边框")
        if not self.topmost_var.get() :
            self.overrideredirect(False)
            print("最小化或者切换到后台，取消隐藏边框")
            if self.hide_id is not None :
                self.after_cancel(self.hide_id)
                print("hide_id canceled")
        # if self.state() == "iconic" :
        #     self.overrideredirect(False)
        #     print("on_minimize")
        #     if self.hide_id is not None :
        #         self.after_cancel(self.hide_id)
        #         print("hide_id canceled")
            # self.iconify()





if __name__ == "__main__" :
    try:
        load_config()
        app = MainApp()
        app.start_audio_listening()
        app.connect_to_llm()
        app.mainloop()
        # app.save_settings()
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("An error occurred:", e)
        input("Press Enter to continue...")
