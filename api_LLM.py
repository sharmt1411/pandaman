import json
import os
import re

from openai import OpenAI
import config
import time


class ApiLLM :

    @staticmethod
    def get_response_deepseek(context, prompts, callback=None) :

        client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
        content = prompts + " "
        messages = [{"role" : "system",
                     "content" : prompts
                     },
                    {"role" : "user", "content" : context}]
        # print(messages)
        print("开始获取response", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            max_tokens=4096,
            temperature=1.0,
            stream=False,
        )
        response = response.choices[0].message.content
        print("开始调用callback,response是", response)
        return  response





if __name__ == '__main__' :
    llm = ApiLLM()
    print(config.MODEL_NAME, config.API_KEY, config.BASE_URL)
    prompts ="""熊猫头表情包是一种流行的网络表情符号，它以一个简单的黑白熊猫头部轮廓为基础，通过不同的表情和文字搭配，在社交媒体和聊天应用中广受欢迎。熊猫头表情包通常用于表达幽默、讽刺、无奈、惊讶等多种情绪，成为网络文化中的一个有趣现象.你现在扮演熊猫头表情包，根据用户的对话，生成符合熊猫头表情的回复"
！！！要求：回复格式[情绪][文本回复]，[情绪]从情绪列表选取，[文本回复]在12个字以内。回复示例：[嘲讽][你真是个小天才！]，[惊讶][卧槽，你居然能说出这种话！]，[害怕][你居然敢说这种话！]，[开心][你真棒！]，[伤心][你真可怕！]，[生气][你真的好气啊！]，[惊喜][你居然说出这种话！]，[厌恶][你真是个坏人！]，[恶心][你真的恶心！]，[难过][你真的难过！]，[亲切][你真亲切！]，[怒][你真的怒！]。以下为可用表情，情绪列表：[嘲讽/默认/]"""
    response =llm.get_response_deepseek("大家好，欢迎来到这里和我聊天", prompts)
    print(response)