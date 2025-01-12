from ragflow import RAGPipeline

# 初始化 RAG 流程
pipeline = RAGPipeline(
    document_path="train.csv",
    vector_db="milvus",
    llm_model="gpt-3.5-turbo"
)

# 加载并处理文档
pipeline.process_documents()

# 提问并生成回答
query = "如何配置 RAGFlow 的混合检索？"
response = pipeline.generate(query)
print(response)
