# Local LLM Chatbot

このアプリはLocal LLMで動くチャットボットアプリです。Wordファイル（.docx）やPDFファイル、Webサイトをドキュメントとして読み込むことができます。

## 使用技術一覧

<p>
<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=fff&style=for-the-badge">
<img src="https://img.shields.io/badge/Ollama-000?logo=ollama&logoColor=fff&style=for-the-badge">
<img src="https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=fff&style=for-the-badge">
</p>

chromaDB

python-docx

requests

pymupdf

beautifulsoup4

## セットアップ手順

本プロジェクトは **Python 3.12** で動作確認を行っています。

1. **Ollamaのダウンロード**

   下記のURLからOllamaをダウンロードしてください。

   https://ollama.com/download

2. **モデルのインストール**

   ```sh
   ollama pull llama3.1:8b
   ```

3. **ライブラリの一括インストール**

   ```sh
   pip install -r requirements.txt
   ```

4. **アプリケーションの起動**

   ```sh
   streamlit run app.py
   ```
