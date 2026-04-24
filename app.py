import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# --- 1. 定数・データ読み込み ---
APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "tasks.json"
JST = ZoneInfo("Asia/Tokyo")

def load_data():
    try:
        with DATA_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"morning": {"ゲスト": ["あさの準備"]}, "night": {"ゲスト": ["よるの準備"]}}

all_data = load_data()

# --- 2. 背景色とスタイルを切り替える関数 ---
def apply_theme(mode):
    if mode == "☀️ あさ":
        bg_color = "#FFFDF0"
        text_color = "#31333F"
        container_bg = "#FFFFFF"
        toast_bg = "#FFFFFF"
        toast_border = "#FF8C00"
        toast_text = "#31333F"
        btn_bg = "#FF4B4B"
        btn_text = "#FFFFFF"
        # 朝：選択肢ボタンの色
        ctrl_bg = "#F0F2F6"      # 未選択の薄いグレー
        ctrl_text = "#31333F"    # 文字はハッキリ
        ctrl_selected = "#FF4B4B" # 選択中は赤
        glow = "rgba(255, 75, 75, 0.2)"
    else:
        bg_color = "#1A1C2C"      # 真っ暗な紺
        container_bg = "#2D303D"  # ★ここを少し明るく
        text_color = "#E0E0E0"
        toast_bg = "#2E3141"
        toast_border = "#00FFCC"
        toast_text = "#FFFFFF"
        btn_bg = "#4A4E69"
        btn_text = "#00FFCC"
        # 夜：選択肢ボタンの色（まぶしくない設定）
        ctrl_bg = "#262730"      # 未選択はコンテナと同じ暗い色
        ctrl_text = "#666666"    # 未選択は文字を沈ませる
        ctrl_selected = "#00FFCC" # 選択中はエメラルド
        glow = "rgba(0, 255, 204, 0.4)"

    st.markdown(f"""
        <style>
        /* 全体の背景 */
        .stApp {{
            background-color: {bg_color} !important;
            transition: background-color 0.5s ease;
        }}
        /* 文字色 */
        h1, h2, h3, p, span, div[data-testid="stCheckbox"] label p {{
            color: {text_color} !important;
        }}
        /* リストの枠 */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: {container_bg} !important;
            border: 1px solid #44475A !important; /* ★うっすらと枠線を追加 */
            border-radius: 15px !important;       /* ★角を少し丸くするとオシャレ */
        }}
        /* トースト */
        div[data-testid="stToast"] {{
            background-color: {toast_bg} !important;
            border: 2px solid {toast_border} !important;
            border-radius: 10px;
        }}
        div[data-testid="stToast"] p {{
            color: {toast_text} !important;
        }}
        /* リセットボタン */
        div.stButton > button {{
            border-radius: 20px !important;
            border: 2px solid {btn_bg} !important;
            background-color: transparent !important;
            color: {btn_text} !important;
            transition: all 0.3s ease !important;
        }}
        div.stButton > button:hover {{
            background-color: {btn_bg} !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 15px {btn_bg} !important;
        }}

        /* --- segmented_control のまぶしさ徹底排除（ここから追加） --- */

        /* 全ボタン共通の文字色をまず暗く沈ませる */
        div[data-testid="stBaseButton-secondary"] p {{
            color: {ctrl_text} !important;
        }}

        /* 未選択ボタンの背景と枠線 */
        div[data-testid="stBaseButton-secondary"] {{
            background-color: {ctrl_bg} !important;
            border: 1px solid {"#ddd" if mode == "☀️ あさ" else "#333"} !important;
        }}

        /* 選択中のボタンを強制発光 */
        div[data-testid="stBaseButton-secondary"][aria-checked="true"] {{
            background-color: transparent !important;
            border: 2px solid {ctrl_selected} !important;
            box-shadow: 0 0 10px {glow} !important;
        }}

        /* 選択中のボタン内の文字色 */
        div[data-testid="stBaseButton-secondary"][aria-checked="true"] p {{
            color: {ctrl_selected} !important;
        }}

        /* ★教えていただいた「最終手段」をここに追加！ */
        div[data-testid="stBaseButton-secondary"] * {{
            color: inherit !important;
        }}
        
        /* チェックボックスのサイズ */
        div[data-testid="stCheckbox"] input[type="checkbox"] {{
            transform: scale(1.4);
        }}
        </style>
    """, unsafe_allow_html=True)

@st.fragment(run_every=30)
def show_current_time(mode):
    # 夜モードの時は時計の横の文字色を少し明るくする調整
    label_color = "#666" if mode == "☀️ あさ" else "#AAA"
    t = datetime.now(JST).strftime("%H:%M")
    st.markdown(f"""
        <div style="display: flex; align-items: baseline; gap: 10px; justify-content: flex-start;">
            <span style="font-size: 1.2rem; color: {label_color};">いまのじかん：</span>
            <span style="font-size: 2.5rem; font-weight: bold;">{t}</span>
        </div>
    """, unsafe_allow_html=True)

def reset_all():
    for key in list(st.session_state.keys()):
        if key.startswith(("cb_", "last_cb_", "all_done_")):
            st.session_state[key] = False
    st.toast("あたらしいミッションを開始しました！")

def render_mission_columns(category_key):
    data = all_data.get(category_key, {})
    if not data:
        st.warning("データがありません")
        return
        
    cols = st.columns(len(data))
    for i, (name, tasks) in enumerate(data.items()):
        with cols[i]:
            st.subheader(f"✨ {name}")
            with st.container(height=400, border=True):
                for task in tasks:
                    cb_key = f"cb_{category_key}_{name}_{task}"
                    last_key = f"last_{cb_key}"
                    
                    checked = st.checkbox(task, key=cb_key)
                    
                    if checked and not st.session_state.get(last_key, False):
                        st.balloons()
                        st.toast(f"やったね！ {task} 完了！")
                    
                    st.session_state[last_key] = checked

                all_checked = all(st.session_state.get(f"cb_{category_key}_{name}_{t}", False) for t in tasks)
                done_key = f"all_done_{category_key}_{name}"
                if all_checked and not st.session_state.get(done_key, False):
                    st.snow()
                    st.success(f"🎉 {name}、ぜんぶクリア！")
                    st.session_state[done_key] = True

# --- 3. メインレイアウト ---
st.set_page_config(page_title="みっしょん", layout="wide")

# モード切替を一番上に配置（これで全てが決まる）
mode = st.segmented_control(
    "じかん帯をえらんでね",
    options=["☀️ あさ", "🌙 よる"],
    default="☀️ あさ",
    key="main_mode"
)

# テーマ（背景色）適用
apply_theme(mode)

# ヘッダー（時計）
show_current_time(mode)

# ミッション表示
if mode == "☀️ あさ":
    render_mission_columns("morning")
else:
    render_mission_columns("night")

# リセットボタン
st.divider()
if st.button("あたらしいミッションをかいしする", on_click=reset_all, use_container_width=True):
    st.balloons()