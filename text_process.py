import os

from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from api_LLM import ApiLLM
import config
import fasterwhisper as fw

def get_prompts(text=None):
    require = (f"！！！要求：回复格式[情绪][文本回复]，[情绪]从情绪列表选取，[文本回复]在12个字以内。"
               f"回复示例：[嘲讽][牛逼死了你！]，[惊讶][卧槽，你居然能说出这种话！]，[害怕][你居然敢说这种话！]，"
               f"[惊喜][你居然说出这种话！]，")
    emotion_list = get_emotions()
    emotion_text = "注意！！！：只能从以下列表选取情绪，列表：["
    for emotion in emotion_list:
        emotion_text += emotion + "/"
    prompts = text + "\n\n" + require + emotion_text+"]"
    return prompts


def get_emotions() :
    path ="./picture/emotion/"
    img_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    image_files = []
    for root, dirs, files in os.walk(path) :
        for file in files :
            # 检查文件扩展名是否在支持的列表中
            if any(file.lower().endswith(ext) for ext in img_extensions) :
                # 去掉后缀名
                file = os.path.splitext(file)[0]
                image_files.append(file)
    return image_files


def text_process(callback=None, phrase_timeout=5) :
    phrase_time = datetime.now()  # 记录上次转换的结束时间
    default_time = datetime.now()   # 用于休眠状态判断，如果连续休眠超过时间，恢复默任图片

    sleep_time = 0.1  # 休眠时间，防止CPU占用过高
    sleep_circle_per_second = int(1/sleep_time)  # 每秒转动多少圈
    default_timeout = 10  # 默认图片切换时间，超过此时间无新内容则认为是新的一句
    default_timeout_circle = default_timeout * sleep_circle_per_second  # 默认图片每秒转动多少圈
    circle_count = 0  # 连续睡眠周期计数

    # phrase_timeout = 5  # 间隔时间，超过此时间无新内容则认为是新的一句
    prompts_setting = config.read_config().get("prompts", "")
    print("prompts_setting", prompts_setting)
    prompts = get_prompts(prompts_setting)
    print("prompts", prompts)
    while True:
        try:
            now = datetime.now()
            raw_text_data = ""
            # text_transformed = ""
            if not fw.text_queue.empty() :  # 队列中有数据，有监测的文本
                phrase_complete = False              # 设置间隔时间提取发送LLM
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout) :
                    phrase_complete = True
                    print("队列中有数据，间隔超时，开始新的转换")
                    phrase_time = now  # 重新计时

                    # Combine audio data from queue
                    raw_text_data = ''.join(fw.text_queue.queue)
                    fw.text_queue.queue.clear()

                    print("请求LLM开始时间", datetime.now())
                    response = ApiLLM.get_response_deepseek(raw_text_data, prompts)
                    print("转换结束时间", datetime.now(),"\n", response)
                    if callback :
                        parts = response.split('][')

                        # 去除方括号
                        emotion = parts[0][1 :]  # 去掉开头的 '['
                        text = parts[1][:-1]  # 去掉结尾的 ']'
                        circle_count = 0  # 重置连续睡眠周期计数
                        callback(emotion, text)

            else:
                # 无数据时间隔一段时间再循环，防止CPU占用过高。检测频率越高，越早触发循环
                if circle_count > default_timeout_circle:
                    # 连续睡眠周期超过默认时间，切换到默认图片
                    circle_count = 0
                    callback(None, None)  # 调用回调函数，切换图片
                else:
                    sleep(sleep_time)
                    circle_count += 1  # 计数



        except Exception as e :
            print("Error:", e)
            break




if __name__ == '__main__':
    config.load_config()
    emotions = get_emotions()
    print(emotions)
    thread = Thread(target=text_process)
    thread.start()
    fw.text_queue.put("你好，我是机器人，请问有什么可以帮助您？")
    sleep(10)

    fw.text_queue.put("大家好啊，欢迎来到我的直播间")
