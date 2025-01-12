from spleeter.separator import Separator
import os

# 初始化分离器，选择2音源模型（人声+乐器）
separator = Separator('spleeter:2stems')

# 指定输入和输出目录
input_audio_path = 'part1.mp3'  # 输入音频文件路径
output_audio_path = 'output/'  # 输出文件夹路径

# 确保输出目录存在
if not os.path.exists(output_audio_path):
    os.makedirs(output_audio_path)

# 开始分离
separator.separate_to_file(input_audio_path, output_audio_path)