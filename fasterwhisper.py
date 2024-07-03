import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from collections import deque

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
text_queue = Queue()


def initial_model():
    global text_queue
    print("开始初始化模型")
    record_timeout = 5   # 默认录音超时时间，限制recognizer最长连续录制时间
    phrase_timeout = 0.5   # 两个小段录音之间有多少空白时间间隔时，我们会将其视为新的一行。在record_timeout》phrase_timeout时，无作用
    energy_threshold = 1000  # 默认能量阈值，禁止自动能量阈值，防止不能自动停止。
    model_size = "small"
    model_path = "./model/" + model_size + ".pt"

    device = "cpu"
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    print("加载模型中，如第一次使用会自动下载模型，预计300M大小。等到提示‘Model loaded，开始监听后’，则加载完毕。")
    audio_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print("Using_device:", device)

    # sr一个有用的功能，即能够检测语音何时结束。
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)  # 麦克风输入源，采样率16000Hz,whisper模型要求16000Hz
    # 自适应噪声，只设置一次，禁止动态
    with source:
        print("Adjusting for ambient noise...energy_threshold:", recorder.energy_threshold)
        recorder.adjust_for_ambient_noise(source, duration=1)
        print("Ready.energy_threshold:", recorder.energy_threshold)

    transcription = deque(maxlen=10)  # 用于保存识别结果的列表
    transcription.append("")    # 初始值为空，防止直接调用-1 索引异常
    # transcription = []  # 用于保存识别结果的列表
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # The last time a recording was retrieved from the queue.
    phrase_time = None

    def record_callback(_, audio: sr.AudioData) -> None :
        # Grab the raw bytes and push it into the thread safe queue.
        print("麦克风有新内容callback,队列新增数据", datetime.now())
        data = audio.get_raw_data()
        data_queue.put(data)

    # 用于在后台持续监听音频源的函数。会将监听音频传入callback后加入转换队列
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    print("Model loaded，开始监听.\n")
    phrase_time = datetime.now()  # 初始时间戳
    while True:
        try:
            now = datetime.now()
            # print("循环监测中")
            if not data_queue.empty() :      # 队列中有数据，有麦克风监测的数据，则进行间隔超时判断
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    # 对列有数据未转写，且间隔超时，则认为是新的一句,
                    # 注意需要允许sr记录的时间record-timeout小于间隔时间phase——timeout，否则会记录到语句结束，每次记录肯定是新的句子
                    phrase_complete = True
                    print("队列中有数据，间隔超时，认为是一句结束，添加新的一行.")

                phrase_time = now  # 重新计时

                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                # 如果是cpu，无法处理int16，需要转换为float32
                # np.int16表示16位有符号整数，其取值范围是-32768到32767。需要归一化，避免使用模型归一化，实际不除不准确
                print("开始转换格式开始时间", datetime.now())
                if device == "cpu":
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)/ 32768
                    # audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    # audio_np = np.frombuffer(audio_data, dtype=np.int16)
                else:
                    audio_np = np.frombuffer(audio_data, dtype=np.int16) / 32768.0

                print("准备转换开始时间", datetime.now())
                segments, info = audio_model.transcribe(audio_np, beam_size=3, language="zh", without_timestamps=True, )
                print("转换结束时间", datetime.now())
                text_transformed = ""
                for segment in segments:
                    # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                    text_transformed += segment.text
                print("识别结果递归完毕", datetime.now())
                # If we detected a pause between recordings, add a new item to our transcription.
                # Other——wise edit the existing one.
                if phrase_complete:
                    transcription.append(text_transformed)
                    text_queue.put(text_transformed)
                    print("队列加入数据",text_transformed, "队列是否为空", text_queue.empty())
                else :
                    transcription[-1] = text_transformed      # 断句没超时，说明是连续的句子，是加上新的词语重复转换，编辑最后一行，
                # print("开始打印", datetime.now())
                for line in transcription :
                    print(line)
                # Flush stdout.
                # print('', end='', flush=True)
                # print("打印结束", datetime.now())
            else:
                # 无数据时间隔一段时间再循环，防止CPU占用过高。检测频率越高，越早触发循环
                sleep(0.1)
        except KeyboardInterrupt :
            print("Ctrl+C，KeyboardInterrupt，退出程序.")
            break
        except Exception as e :
            print("Error:", e)
            break

    print("\n\nTranscription:")
    for line in transcription :
        print(line)


if __name__ == "__main__" :
    initial_model()