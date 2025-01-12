# 安装 pydub
```shell
pip3 install pydub
```

# 安装 ffmpeg
出现如下如下错误:
```shell
FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe'
```
缺少ffmpeg，如下安装:
```shell
1. 在 https://www.ffmpeg.org/download.html 下载对应系统的二进制ffmpeg和ffprobe
2. 放在一个路径, 然后添加到环境变量PATH中, 并使其生效
```