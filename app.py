import streamlit as st
from search import call_search  # search.py から call_search をインポート
from datetime import datetime
import pandas as pd
import io

# ページ設定は最初に記述
st.set_page_config(
    page_title="Search Automation App",
    layout="wide",
)

# アプリのタイトル
st.title("Search Automation App")


# ログファイル名の生成
def generate_default_log_filename():
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M.csv")


# パスワード認証機能
def authenticate(password):
    """シンプルなパスワード認証機能"""
    # Streamlit Secrets から正しいパスワードを取得
    correct_password = st.secrets["APP_PASSWORD"]
    return password == correct_password


# サイドバーでパスワード入力
password = st.sidebar.text_input("パスワードを入力してください", type="password")

if authenticate(password):
    # 認証成功時のアプリ
    st.sidebar.success("認証に成功しました！")
    
    # サイドバーで検索設定を受け取る
    with st.sidebar:
        st.header("検索設定")
        keywords_input = st.text_input("検索キーワード（カンマ区切り）", value="エンジニア, 社員紹介, 事例")
        num_results = st.slider("取得する結果の最大件数", min_value=1, max_value=200, value=10)
        engine = st.selectbox("検索エンジン", options=["google", "bing", "yahoo"], index=0)
        hl = st.text_input("言語設定", value="ja")
        default_log_filename = "HR-keyword-search_" + generate_default_log_filename()  # デフォルトのログファイル名を生成
        log_filename = st.text_input("ログファイル名", value=default_log_filename)  # デフォルトを表示
        debug_mode = st.checkbox("デバッグモード", value=True)

    # ユーザーが検索を実行する
    if st.button("検索を開始"):
        # 検索キーワードをリスト形式に変換
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        
        if not keywords:
            st.error("検索キーワードを1つ以上入力してください。")
        else:
            # 検索処理を実行
            st.write("検索中...")
            try:
                urls = call_search(
                    keywords=keywords,
                    num_results=num_results,
                    engine=engine,
                    hl=hl,
                    log_filename=log_filename,  # ユーザーが入力したログファイル名を使用
                    debug_mode=debug_mode,
                    use_streamlit=True,
                )
                if urls:
                    st.success("検索が完了しました。以下が結果です。")
                    for url in urls:
                        st.write(f"- [{url}]({url})")
                    
                    # 検索キーワードを先頭行に含める
                    csv_buffer = io.StringIO()
                    
                    # キーワード情報を先頭に書き込み、URLをそのまま改行区切りで追加
                    csv_buffer.write(f"検索キーワード: {', '.join(keywords)}\n")
                    csv_buffer.write("\n".join(urls))  # URL リストを改行区切りで追加
                    
                    # ダウンロードボタン
                    st.download_button(
                        label="CSVダウンロード",
                        data=csv_buffer.getvalue(),
                        file_name=log_filename,  # ユーザーが指定したログファイル名を使用
                        mime="text/csv",
                    )
                else:
                    st.warning("検索結果がありません。")
            except Exception as e:
                st.error(f"検索中にエラーが発生しました: {e}")

else:
    # 認証失敗時のメッセージ
    st.sidebar.error("認証に失敗しました。正しいパスワードを入力してください。")
