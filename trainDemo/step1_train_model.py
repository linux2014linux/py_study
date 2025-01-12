import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments

print(f"MPS available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")
device = torch.device("mps")

model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="mps")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token


def preprocess_function(examples):
    prompts = [
        f"### Instruction:\n{ins}\n### Input:\n{inp}\n### Response:\n"
        for ins, inp in zip(examples['instruction'], examples['input'])
    ]
    model_inputs = tokenizer(
        prompts,
        max_length=512,
        truncation=True,
        padding="max_length"
    )

    labels = tokenizer(
        examples["output"],
        max_length=512,
        truncation=True,
        padding="max_length"
    )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


dataset = load_dataset('json', data_files='train.json')
tokenized_dataset = dataset.map(preprocess_function, batched=True)


lora_config = LoraConfig(
    r=16,  # 秩维度
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  # 针对Llama架构
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
training_args = TrainingArguments(
    output_dir="./text2sql-output",
    eval_strategy="steps",
    eval_steps=200,
    save_strategy="steps",
    save_steps=500,
    learning_rate=2e-5,
    per_device_train_batch_size=2,  # M2 Pro建议值
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_steps=50,
    fp16=False,  # cuda 设置为 True, metal 设置为 False
    bf16=True,  # metal 设置为 True
    report_to="none"
)


# 继承 Trainer
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        # 计算交叉熵损失
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()

        loss_fct = torch.nn.CrossEntropyLoss()
        loss = loss_fct(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1)
        )
        return (loss, outputs) if return_outputs else loss


trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["train"],
    data_collator=lambda data: {
        "input_ids": torch.stack([torch.tensor(d["input_ids"]) for d in data]),
        "attention_mask": torch.stack([torch.tensor(d["attention_mask"]) for d in data]),
        "labels": torch.stack([torch.tensor(d["labels"]) for d in data])
    }
)

trainer.train()

# 保存LoRA权重
model.save_pretrained("./text2sql-lora")

# 合并并保存完整模型
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./text2sql-full-model")
tokenizer.save_pretrained("./text2sql-full-model")
