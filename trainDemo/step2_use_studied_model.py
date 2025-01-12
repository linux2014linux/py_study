import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

device = torch.device("mps")
model_name = "./text2sql-full-model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="mps", offload_state_dict=False)
model.generation_config = GenerationConfig.from_pretrained(model_name)
model.generation_config.pad_token_id = model.generation_config.eos_token_id


def generate_query(text):
    prompt = f"### Instruction:\n将用户请求转换为数据库查询\n### Input:\n{text}\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)

    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.1,
        do_sample=True,
        attention_mask=inputs["attention_mask"],
        num_beams=3,  # 使用束搜索
        early_stopping=True,  # 提前终止
        no_repeat_ngram_size=2,  # 防止重复
        length_penalty=0.8
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("### Response:")[-1].strip()


# 测试示例
print(generate_query("显示2024年Q1退货率超过5%的产品"))
# 预期输出：SELECT product_id, product_name FROM orders
#           WHERE year=2024 AND quarter=1
#           GROUP BY product_id HAVING (COUNT(returned)/COUNT(*)) > 0.05;
