import os
import sys

MODEL_NAME = ''
API_KEY = ''
BASE_URL = ''
POSITION = {"background_x" : 140, "background_y" : 97, "bubble_x" : 0, "bubble_y" : 0, "text_x" : 27, "text_y" : 23}


def create_default_config(config_file):
    default_config = """MODEL_NAME = deepseek-chat
API_KEY = your_api_key_here
BASE_URL = https://api.deepseek.com
background_x = 140
background_y = 97
bubble_x = 0
bubble_y = 0
text_x= 27
text_y =23
prompts = "熊猫头表情包是一种流行的网络表情符号，它以一个简单的黑白熊猫头部轮廓为基础，通过不同的表情和文字搭配，在社交媒体和聊天应用中广受欢迎。熊猫头表情包通常用于表达幽默、讽刺、无奈、惊讶等多种情绪，成为网络文化中的一个有趣现象.你现在扮演熊猫头表情包，根据用户的对话，生成符合熊猫头表情的回复。"
#prompts 自定义修改不要手动换行，否则会导致生成的回复不完整，直接删掉一直敲，自动换行可以，不要敲回车

#deepseek免费送500万token，申请地址：https://platform.deepseek.com/api_keys 直接创建黏贴进来就可以了
# 如果是openai，需要替换为openai的API_KEY及相关参数
# MODEL_NAME = "gpt-4o"
# API_KEY = "你的apikey"
# BASE_URL = "https://api.openai.com/v1"
"""
    try:
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(default_config)
        print(f"Created default config file: {config_file}")
    except Exception as e:
        print(f"Error creating file {config_file}: {e}")


def read_config(config_file='config.txt'):
    config = {}
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    config[key] = value
        file.close()
        return config
    except FileNotFoundError:
        print(f"Error: {config_file} does not exist.")
        create_default_config(config_file)
        return None
    except Exception as e:
        print(f"Error reading file {config_file}: {e}")
    return None

def load_config():
    global MODEL_NAME, API_KEY, BASE_URL, POSITION

    if getattr(sys, 'frozen', False) :
        # 如果是打包后的可执行文件
        base_dir = os.path.dirname(sys.executable)
        print(f"Running in frozen mode, base directory: {base_dir}")
    else :
        # 如果是源代码
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Running in source mode, base directory: {base_dir}")

    config_file = os.path.join(base_dir, 'config.txt')

    config = read_config(config_file)
    if config :
        MODEL_NAME = config.get('MODEL_NAME', 'default_model_name')
        API_KEY = config.get('API_KEY', 'default_api_key')
        BASE_URL = config.get('BASE_URL', 'https://default.url.com')
        background_x = config.get('background_x', 140)
        background_y = config.get('background_y', 97)
        bubble_x = config.get('bubble_x', 0)
        bubble_y = config.get('bubble_y', 0)
        text_x = config.get('text_x', 27)
        text_y = config.get('text_y', 23)
        POSITION = {"background_x" : background_x, "background_y" : background_y, "bubble_x" : bubble_x,
                    "bubble_y" : bubble_y, "text_x" : text_x, "text_y" : text_y}
        print("config载入成功")
        # print("load position:", POSITION)
        # print(isinstance(BASE_URL, str))

        # print(f"Model Name: {MODEL_NAME}")
        # print(f"API Key: {API_KEY}")
        # print(f"Base URL: {BASE_URL}")
    else :
        # 如果config为空，尝试重新读取配置文件
        config = read_config(config_file)
        if config :
            MODEL_NAME = config.get('MODEL_NAME', 'default_model_name')
            API_KEY = config.get('API_KEY', 'default_api_key')
            BASE_URL = config.get('BASE_URL', 'https://default.url.com')
            background_x = config.get('background_x', 140)
            background_y = config.get('background_y', 97)
            bubble_x = config.get('bubble_x', 0)
            bubble_y = config.get('bubble_y', 0)
            text_x = config.get('text_x', 27)
            text_y = config.get('text_y', 23)
            POSITION = {"background_x" : background_x, "background_y" : background_y, "bubble_x" : bubble_x,
                        "bubble_y" : bubble_y, "text_x" : text_x, "text_y" : text_y}
            print("再次初始化变量成功")
            # print(f"Model Name: {MODEL_NAME}")
            # print(f"API Key: {API_KEY}")
            # print(f"Base URL: {BASE_URL}")
        else :
            print("Failed to read configuration.")
            # 这里可以添加一些默认配置，比a如从环境变量中读取


def save_config(config_dict, config_file='config.txt'):
    # global MODEL_NAME, API_KEY, BASE_URL
    content = ""
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    for key, value in config_dict.items():
                        if line.startswith(key):
                            line = f"{key} = {value}\n"
                            print(f"更新{key}",line)
                            break
                    content = content + line
                else:
                    content = content + line

        with open(config_file, 'w', encoding='utf-8') as file:
            if content != "":
                file.write(content)
                file.close()
            else:
                print("config内容为空，不保存")
        print(f"Saved config to {config_file}")
    except Exception as e:
        print(f"save_config Error saving file {config_file}: {e}")


if __name__ == '__main__':
    print("Testing config.py,之前--Position", POSITION)
    load_config()
    print("第一次加载，", POSITION)
    save_config({'background_x': 140, 'background_y': 97, 'bubble_x': 0, 'bubble_y': 0, 'text_x': 27, 'text_y': 23})
    load_config()
    config = read_config()
    print("prompt,", config.get('prompts', '无'))
    print("保存后", POSITION)
