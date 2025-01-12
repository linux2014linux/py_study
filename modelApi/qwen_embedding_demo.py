#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问Embedding API调用示例
使用APP_KEY调用千问的文本向量化服务
"""

from typing import Dict, Any

import requests


class QwenEmbeddingClient:
    def __init__(self, app_key: str = "YOUR_APP_KEY",
                 api_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"):
        self.app_key = app_key
        self.api_base_url = api_base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {app_key}'
        }

    def generate_embedding(self, text: str, model: str = "text-embedding-v4") -> Dict[str, Any]:
        payload = {
            "model": model,
            "input": text,
            "encoding_format": "float"
        }

        try:
            response = requests.post(
                self.api_base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }


def main():
    client = QwenEmbeddingClient()
    text = "人工智能是计算机科学的一个重要分支"
    result = client.generate_embedding(text)
    print(f"返回: {result}")


if __name__ == "__main__":
    main()
