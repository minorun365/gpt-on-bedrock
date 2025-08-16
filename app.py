import asyncio
import streamlit as st
from strands import Agent

# エージェントを作成
agent = Agent("openai.gpt-oss-120b-1:0")

# ページタイトルと入力欄を表示
st.title("GPT on Bedrock")
prompt = st.text_input("Strands Agent経由でGPT-OSS 120Bに質問しよう！")

# 非同期ストリーミング処理
async def process_stream(prompt, container):
    text_holder = container.empty()
    response = ""
    
    # エージェントからのストリーミングレスポンスを処理    
    async for chunk in agent.stream_async(prompt):
        if isinstance(chunk, dict):
            event = chunk.get("event", {})
            
            # テキストを抽出してリアルタイム表示
            if text := chunk.get("data"):
                response += text
                text_holder.markdown(response)

# ボタンを押したら生成開始
if st.button("質問"):
    if prompt:
        with st.spinner("考え中…"):
            container = st.container()
            asyncio.run(process_stream(prompt, container))