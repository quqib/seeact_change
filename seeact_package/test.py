import litellm
litellm.set_verbose = True

response = litellm.completion(
    model="ByteDance-Seed/Seed-OSS-36B-Instruct",  # 确认模型名称正确
    messages=[{"role": "user", "content": "Hello"}],
    custom_llm_provider="openai",
    api_base="https://api.siliconflow.cn/v1",
    api_key="sk-djopgpiaqvbtecyekaqftozuxkkpartbhjygxbfdjuazwpkz",   # 直接填入密钥，避免环境变量问题
    max_tokens=100
)
print(response)


