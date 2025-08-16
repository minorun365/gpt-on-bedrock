import os
import asyncio
import streamlit as st
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# ページ設定
st.set_page_config(
    page_title="Strands with Bedrock",
    layout="wide"
)

# Streamlitシークレットを環境変数に設定
os.environ['AWS_ACCESS_KEY_ID'] = st.secrets['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = st.secrets['AWS_SECRET_ACCESS_KEY']
os.environ['AWS_DEFAULT_REGION'] = st.secrets['AWS_DEFAULT_REGION']
os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_API_KEY']

# 利用可能なモデルの定義
AVAILABLE_MODELS = {
    "GPT-OSS 120B": "openai.gpt-oss-120b-1:0",
    "Llama 4 Marverick": "us.meta.llama4-maverick-17b-instruct-v1:0",
    "DeepSeek-R1": "us.deepseek.r1-v1:0",
    "Nova Premier（MCP対応）": "us.amazon.nova-premier-v1:0",
    "Claude Opus 4.1（MCP対応）": "us.anthropic.claude-opus-4-1-20250805-v1:0"
}

# サイドバーでモデル選択
with st.sidebar:
    selected_model_name = st.selectbox(
        "モデル",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
    )
    selected_model = AVAILABLE_MODELS[selected_model_name]

mcp = MCPClient(lambda: streamablehttp_client(
    "https://mcp.tavily.com/mcp/?tavilyApiKey=" + st.secrets['TAVILY_API_KEY']
))

# メインエリア
st.title("Strands with Bedrock")
prompt = st.text_input(f"好きなLLMに質問しよう！")

# 非同期ストリーミング処理
async def process_stream(prompt, container):
    text_holder = container.empty()
    response = ""

    with mcp:
        tools = []
        if "MCP対応" in selected_model_name:
            tools = mcp.list_tools_sync()
        agent = Agent(
            model=selected_model,
            system_prompt="思考も回答も日本語で行って。必要あればWeb検索ツールを使って。ちなみに現在2025年8月です。",
            tools=tools
        )
    
        # エージェントからのストリーミングレスポンスを処理    
        async for chunk in agent.stream_async(prompt):
            if isinstance(chunk, dict):
                event = chunk.get("event", {})

                # ツール実行を検出して表示
                if "contentBlockStart" in event:
                    tool_use = event["contentBlockStart"].get("start", {}).get("toolUse", {})
                    tool_name = tool_use.get("name")
                    
                    # バッファをクリア
                    if response:
                        text_holder.markdown(response)
                        response = ""

                    # ツール実行のメッセージを表示
                    container.info(f"リモートMCPで {tool_name} ツールを実行中…")
                    text_holder = container.empty()
                
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