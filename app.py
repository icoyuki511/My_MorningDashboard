import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. データの読み込み
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "tasks.json"
JST = ZoneInfo("Asia/Tokyo")

def load_data():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)

data = load_data()

@st.fragment(run_every=30)  # 30秒ごとにこの関数だけ再実行
def show_current_time():
    t = datetime.now(JST).strftime("%H:%M")
    st.metric("いまの時間", t)  # または st.markdown で大きい文字

# 2. UI設定
st.set_page_config(page_title="Morning Mission", layout="wide")

st.markdown(
    """
    <style>
    /* TODOチェックボックスの文字サイズを大きくする */
    div[data-testid="stCheckbox"] label p {
        font-size: 1.2rem !important;  /* ← ここを 1.1〜1.5 で調整 */
        font-weight: 600 !important;
        line-height: 1.45 !important;
    }

    /* チェックボックス本体も少し大きく見せたい場合 */
    div[data-testid="stCheckbox"] input[type="checkbox"] {
        transform: scale(1.15);
        transform-origin: left center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. リセット処理用の関数
def reset_all():
    # session_state内の各チェックボックスの値を直接Falseに書き換える
    for name, tasks in data.items():
        for task in tasks:
            key = f"cb_{name}_{task}"
            st.session_state[key] = False

# 4. ヘッダー
col_t1, col_t2 = st.columns([1, 1])
with col_t1:
    st.title("☀️あさのミッション")
with col_t2:
    show_current_time()

# 6. リセットボタン
st.divider()
_, mid, _ = st.columns([1, 2, 1])
with mid:
    if st.button(
        "みんなの新しい朝スタート！",
        on_click=reset_all,
        type="primary",
        use_container_width=True,
    ):
        st.toast("新しい朝がスタートしました！")
        st.balloons()

# 5. TODOリスト表示
cols = st.columns(len(data))

for i, (name, tasks) in enumerate(data.items()):
    with cols[i]:
        st.subheader(f"✨ {name}")
        # HTMLのdivで囲んでスクロール可能にする
        with st.container(height=410, border=True):  # 高さは好みで
        
            for task in tasks:
                key = f"cb_{name}_{task}"
                
                # session_stateにキーがない場合は初期化
                if key not in st.session_state:
                    st.session_state[key] = False
                
                # チェックボックスを表示
                # on_changeではなく、返り値を見て演出を実行
                checked = st.checkbox(task, key=key)
                
                # 前回の状態を保存して、新しくチェックされた時だけ風船
                last_key = f"last_{key}"
                if checked and not st.session_state.get(last_key, False):
                    st.balloons()
                    st.toast(f"やったね！ {task} 完了！")
                
                st.session_state[last_key] = checked

            all_checked = all(
                st.session_state.get(f"cb_{name}_{task}", False) for task in tasks
            )
            all_done_key = f"all_done_{name}"
            was_all_done = st.session_state.get(all_done_key, False)

            if all_checked and not was_all_done:
                st.snow()

            st.session_state[all_done_key] = all_checked

