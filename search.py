import os
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import urllib3
import re
from dotenv import load_dotenv
from print_utils import debug_print  # 共通のログ関数をインポート

import streamlit as st

# .envファイルを読み込む
load_dotenv()

# SerpApiのAPIキーを環境変数から取得
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_API_KEY:
    raise ValueError("APIキーが設定されていません。環境変数 'SERPAPI_API_KEY' を設定してください。")

# InsecureRequestWarningを無効にする
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def call_search(keywords, num_results=5, engine="google", hl="ja", log_filename="debug_log.txt", debug_mode=False, use_streamlit=False):
    """
    キーワードでGoogle検索を行い、取得した結果のURLリストを返す。
    
    Args:
        keywords (list): 検索キーワードのリスト。
        num_results (int): 取得する結果の最大件数。
        engine (str): 使用する検索エンジン。デフォルトは "google"。
        hl (str): 言語設定。デフォルトは "ja"。
        log_filename (str): ログファイルの名前。
        debug_mode (bool): デバッグモードが有効かどうか。
        use_streamlit (bool): Streamlit環境でのデバッグ出力を有効にするか。
    Returns:
        list: 検索結果から取得したURLのリスト。
    """
    query = " ".join(keywords)
    debug_print(f"[DEBUG - call_search] Query: {query}, Engine: {engine}, HL: {hl}, Number of Results: {num_results}", log_filename, debug_mode, use_streamlit)

    params = {
        "engine": engine,
        "q": query,
        "hl": hl,
        "num": num_results,
        "api_key": SERPAPI_API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])

    # デバッグ用に検索結果の数を出力
    debug_print(f"[DEBUG - call_search] Number of organic results: {len(organic_results)}", log_filename, debug_mode, use_streamlit)

    # URLリストのみを返す
    urls = [result.get("link") for result in organic_results if result.get("link")]
    debug_print(f"[DEBUG - call_search] Extracted URLs: {urls}", log_filename, debug_mode, use_streamlit)
    return urls


def main(keywords, num_results, engine, hl, log_filename="debug_log.txt", debug_mode=False, use_streamlit=False):
    """
    メイン処理。キーワードを使用して検索し、結果を表示。
    
    Args:
        keywords (list): 検索キーワードのリスト。
        num_results (int): 取得する結果の最大件数。
        engine (str): 使用する検索エンジン。
        hl (str): 言語設定。
        log_filename (str): ログファイルの名前。
        debug_mode (bool): デバッグモードが有効かどうか。
        use_streamlit (bool): Streamlit環境でのデバッグ出力を有効にするか。
    """
    debug_print("[DEBUG - main] Starting search process", log_filename, debug_mode, use_streamlit)
    urls = call_search(keywords, num_results, engine, hl, log_filename, debug_mode, use_streamlit)
    if urls:
        debug_print("[DEBUG - main] Search results found", log_filename, debug_mode, use_streamlit)
        print("検索結果のURLリスト:")
        for url in urls:
            print(url)
    else:
        debug_print("[ERROR - main] No search results found", log_filename, debug_mode, use_streamlit)
        print("検索結果がありません。")


if __name__ == "__main__":
    # Streamlit UI
    st.title("Search Automation")

    with st.sidebar:
        st.header("検索設定")
        keywords_input = st.text_input("検索キーワード（カンマ区切り）", "エンジニア, 社員紹介, 事例")
        num_results = st.slider("取得する結果の最大件数", 1, 50, 5)
        engine = st.selectbox("検索エンジン", ["google", "bing", "yahoo"])
        hl = st.text_input("言語設定", "ja")
        debug_mode = st.checkbox("デバッグモード", value=False)

    if st.button("検索開始"):
        keywords = [k.strip() for k in keywords_input.split(",")]
        main(keywords, num_results, engine, hl, debug_mode=debug_mode, use_streamlit=True)
