# mac m1等芯片环境
spleeter依赖tensorflow等东西, 需要特殊处理

```shell
# 先下载这个
https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-arm64.pkg
```
```python
import platform
platform.platform()
```
输出必须是arm架构信息才行, 这一步的作用是校正后续tensorflow运行环境与mac的m等芯片相同.

安装conda
```shell
brew install miniforge
# 这里安装3.8, 安装3.9后面spleeter无法安装成功
conda create -n spleeter-env python=3.8
# 激活并进入运行环境, 后续的执行都必须在这个环境里面执行才行
conda activate spleeter-env
conda install -c apple tensorflow-deps
pip install tensorflow-macos tensorflow-metal
pip install spleeter
```
上述的安装都是在conda环境中做的, 所以后续执行tensorflow等相关的python都需要进入该环境。
**激活并进入运行环境, 后续的执行都必须在这个环境里面执行才行**
```shell
# 查看有哪些环境
conda info --envs

# 进入指定环境
conda activate spleeter-env

# 退出conda
conda deactivate

# 关闭 Conda 自动激活
conda config --set auto_activate_base false

```