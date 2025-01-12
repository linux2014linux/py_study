
from pydub import AudioSegment

# 加载MP3文件
audio = AudioSegment.from_mp3("./input/0.5-1min.mp3")

# 指定切割的起始和结束时间（毫秒）
start_time = 0.5 * 60 * 1000       # 切割起始点
end_time = 1 * 60 * 1000     # 切割结束点，例如60秒（30000毫秒）

# 切割音频
cropped_audio = audio[start_time:end_time]

# 保存切割后的音频文件
cropped_audio.export("./output/0.5-1min.mp3", format="mp3")