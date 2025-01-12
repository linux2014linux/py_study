
from pydub import AudioSegment

# 加载MP3文件
audio = AudioSegment.from_mp3("audio_1.mp3")

# 指定切割的起始和结束时间（毫秒）
start_time = (60 + 52) * 60 * 1000       # 切割起始点
end_time = (60 + 54) * 60 * 1000     # 切割结束点，例如30秒（30000毫秒）

# 切割音频
cropped_audio = audio[start_time:end_time]

# 保存切割后的音频文件
cropped_audio.export("part1.mp3", format="mp3")