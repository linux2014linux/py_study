
### 安装rust环境
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh

### 进入conda环境
```shell
# 创建python3.10环境
conda create --name py10 python=3.10
# 进入py10环境
conda activate py10
```
**注意: 后续的pip和python执行动作均在该环境执行。**

### 配置模型下载工具 
注意用git下载需要配置git-lfs否则大文件无法下载成功，并且huggingface要求配置ssh-key等信息，我这里没有配置成功，使用了huggingface的工具下载模型。
```shell
pip install huggingface_hub
pip install hf_transfer
```

### 下载模型
```shell
# 下载模型
huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Llama-8B
# 下载后的模型默认在~/.cache/huggingface/hub/, 模型命名如下
drwxr-xr-x  6 ll  staff   192B  2 19 21:58 models--deepseek-ai--DeepSeek-R1-Distill-Llama-8B
drwxr-xr-x  5 ll  staff   160B  2 20 13:42 models--deepseek-ai--DeepSeek-R1-Distill-Qwen-1.5B
```
注意, 在代码使用时保持和huggingface模型名相同, 如deepseek-ai/DeepSeek-R1-Distill-Llama-8B, 不要写成下载后的文件夹名称。

### 下载数据集
```shell
huggingface-cli download --repo-type text2sql --local-dir /Users/ll/Work/study/py_study/trainDemo/text2sql Mudasir692/text-to-sql
```
注意, 代码中数据集参数是路径不是文件名

### 安装依赖
pip install torch
pip install unsloth -- 无法安装在m2 mac13环境
pip install transformers
pip install datasets

### FAQ
* python3.8运行会报错
```
RuntimeError: Failed to import transformers.models.auto because of the following error (look up to see its traceback): 
/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/tokenizers/tokenizers.abi3.so: undefined symbol: PyInterpreterState_Get
```
参考链接 https://github.com/huggingface/tokenizers/issues/1691, 替换成python3.10就可以了。

* 