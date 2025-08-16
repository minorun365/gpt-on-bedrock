import os
import asyncio
import streamlit as st
from strands import Agent

# ページ設定
st.set_page_config(
    page_title="GPT on Bedrock",
    layout="wide"
)

# Streamlitシークレットを環境変数に設定
os.environ['AWS_ACCESS_KEY_ID'] = st.secrets['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = st.secrets['AWS_SECRET_ACCESS_KEY']
os.environ['AWS_DEFAULT_REGION'] = st.secrets['AWS_DEFAULT_REGION']

# 利用可能なモデルの定義
AVAILABLE_MODELS = {
    "GPT-OSS 120B": "openai.gpt-oss-120b-1:0",
    "Nova Premier": "us.amazon.nova-premier-v1:0",
    "Llama 4 Marverick": "us.meta.llama4-maverick-17b-instruct-v1:0",
    "DeepSeek-R1": "us.deepseek.r1-v1:0",
    "Claude Opus 4.1": "us.anthropic.claude-opus-4-1-20250805-v1:0"
}

# サイドバーでモデル選択
with st.sidebar:
    selected_model_name = st.selectbox(
        "モデル",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]

# エージェントを作成（選択されたモデルを使用）
agent = Agent(selected_model)

# メインエリア
st.title("Strands with Bedrock")
prompt = st.text_input(f"好きなLLMに質問しよう！")

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
        with st.spinner("考え中…（利用者が多いと応答まで時間がかかります）"):
            container = st.container()
            asyncio.run(process_stream(prompt, container))