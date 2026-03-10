import streamlit as st
from openai import OpenAI
import chromadb
from docx import Document
import requests
import fitz

# ChromaDBの設定
DB_DIR = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=DB_DIR)

if "collection" not in st.session_state:
    st.session_state.collection = chroma_client.get_or_create_collection(
        name="local_docs"
    )

# Ollamaからインストールしたモデルを使ったベクトル化関数
def ollama_embed(text):
    r = requests.post(
        "http://localhost:12000/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    data = r.json()
    return data["embedding"]

# Wordファイルを読み込む関数
def load_word_document(file):
    return "\n".join(para.text for para in Document(file).paragraphs)

# PDFファイルを読み込む関数
def load_pdf_pymupdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text

# テキスト分割関数
def split_text(text):
    chunk_size = 600
    overlap = 100
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# サイドバーの設定
st.set_page_config(page_title="Local LLM Chat")

st.sidebar.title("設定")
model = st.sidebar.text_input("モデル名",value="llama3.1:8b")
temperature = st.sidebar.slider("temperature", 0.0, 2.0, 0.3, 0.1)

system_prompt = st.sidebar.text_area(
    "System Prompt",
    "あなたは有能なアシスタントです。日本語で回答してください。",
)

# Word、PDFファイルのアップロード
uploaded_files = st.sidebar.file_uploader(
    "Word、PDFファイルをアップロード(.docx, .pdf)",
    type=["docx", "pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("インデックス作成"):
    for file in uploaded_files:
        if file.name.endswith(".docx"):
            text = load_word_document(file)
        elif file.name.endswith(".pdf"):
            text = load_pdf_pymupdf(file)
        chunks = split_text(text)
        for i,chunk in enumerate(chunks):
            embed = ollama_embed(chunk)
            st.session_state.collection.add(
                documents=[chunk],
                embeddings=[embed],
                ids=[f"{file.name}_{i}"]
            )
    st.sidebar.success("インデックス作成完了")

# タイトル
st.title("Local LLM Chat")

# 会話の履歴を保管
if "messages" not in st.session_state:
    st.session_state.messages = []

# 会話の履歴をリセットするボタン
if st.sidebar.button("会話をリセット"):
    st.session_state.messages = []

# 会話の履歴を表示
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

prompt = st.chat_input("メッセージを入力")

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:12000/v1"
)
if prompt:

    # ユーザーのプロンプト表示
    with st.chat_message("user"):
        st.write(prompt)

    # RAG検索
    query_embed = ollama_embed(prompt)
    results = st.session_state.collection.query(
        query_embeddings=[query_embed],
        n_results=5
    )

    if results["documents"]:
        context_text = "\n".join(results["documents"][0])
        rag_prompt = f"""
        以下は関連ドキュメントの抜粋です。
        {context_text}
        この情報を参考に以下の質問に答えてください。
        {prompt}
        """
        final_user_prompt = rag_prompt
    else:
        final_user_prompt = prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    prompt_message = []

    # if system_prompt.strip():
    #     messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    # else:
    #     messages = st.session_state.messages
    if system_prompt.strip():
        prompt_message.append({"role": "system", "content": system_prompt})

    # 過去の履歴を追加（ただし、今追加したばかりの最新の prompt 以外）
    # これにより過去の文脈をLLMに伝える
    prompt_message.extend(st.session_state.messages[:-1])

    # 最新の質問だけを「ドキュメント情報付き」のプロンプトに差し替えて追加
    prompt_message.append({"role": "user", "content": final_user_prompt})

    # LLMの返答を表示
    with st.chat_message("assistant"):
        placeholder = st.empty()
        stream_response = ""
        stream = client.chat.completions.create(
            model=model,
            messages=prompt_message,
            temperature=temperature,
            stream=True
        )
        for chunk in stream:
            stream_response += chunk.choices[0].delta.content
            placeholder.write(stream_response)  
    
    # 会話の履歴を保存
    st.session_state.messages.append({"role": "assistant", "content": stream_response})