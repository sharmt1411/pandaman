# pandaman

## 熊猫头表情包直播助手
## Panda Head Emoji Live Streaming Assistant

给直播间添点趣味和不确定的趣味性
Adding fun and unpredictable entertainment to live streams

### 功能
- 自动从picture/emotion目录下读取表情包图片，并使用AI选择播放
- 自动识别用户语音，并回复
- 支持自定义角色性格，在config中的prompts 中修改
- 支持自定义图片，按照情绪格式命名，方便AI识别选择
- 支持GIF格式表情包

### Features
- Automatically reads emoji images from the picture/emotion directory and uses AI to select and play them
- Automatically recognizes user's voice and responds
- Supports customization of character personalities, modify in the prompts section of the config
- Supports custom images, named according to emotion format for easy AI recognition and selection
- Supports GIF format emojis

### 整体架构 
整体使用faster—whisper 实现音频转文字
使用deepseek 进行角色模拟
### Overall Architecture
Uses faster-whisper for audio-to-text conversion
Uses deepseek for character simulation

### 展示图片
### Display Images
直播画面
![image](display/演示.gif)
![image](display/示例1.png)
![image](display/示例2.png)
![image](display/软件界面.png)


