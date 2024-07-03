# pandaman
## 熊猫头表情包直播助手


### 功能
- 自动从picture/emotion目录下读取表情包图片，并使用AI选择播放
- 自动识别用户语音，并回复
- 支持自定义角色性格，在config中的prompts 中修改
- 支持自定义图片，按照情绪格式命名，方便AI识别选择
- 支持GIF格式表情包


### 整体架构 
整体使用faster—whisper 实现音频转文字
使用deepseek 进行角色模拟
