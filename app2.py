import streamlit as st
import random
import re
from pathlib import Path

# --- Настройки страницы ---
st.set_page_config(page_title="Учить слова", page_icon="📚", layout="centered")

# --- Стилизация фона и кнопок ---
st.markdown("""
    <style>
        body {
            background-color: #fdf6f0;
        }
        .stApp {
            background-color: #fdf6f0;
        }
        .main-button {
            display: inline-block;
            background: #ffb703;
            color: white;
            font-weight: bold;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 22px;
            text-decoration: none;
            transition: background 0.3s;
        }
        .main-button:hover {
            background: #fb8500;
        }
    </style>
""", unsafe_allow_html=True)

# --- Парсинг слов ---
def parse_words(md_text):
    entries = md_text.split("## 🔤 ")
    return [entry.strip() for entry in entries if entry.strip()]

# --- Главный экран ---
def main_screen():
    st.title("📚 Учим английские слова")

    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    if st.button("🚀 Начать учить слова", use_container_width=True):
        st.session_state["screen"] = "study"
        st.session_state["current_index"] = 0
        st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=50)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Экран изучения слов ---
def study_screen():
    index = st.session_state["current_index"]
    words = st.session_state["shuffled_words"]

    if index < len(words):
        word_md = "## 🔤 " + words[index]

        st.markdown(f"""
            <div style="
                background-color: #ffffff;
                padding: 25px;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            ">
                {word_md}
            </div>
        """, unsafe_allow_html=True)

        st.progress((index + 1) / 50)
        st.caption(f"Слово {index + 1} из 50")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️ Вперёд", use_container_width=True):
                st.session_state["current_index"] += 1
                st.rerun()
        with col2:
            if st.button("🏠 На главный экран", use_container_width=True):
                st.session_state["screen"] = "main"
                st.rerun()
    else:
        st.subheader("🎉 Вы выучили все 50 слов!")
        st.markdown("### Вот они:")
        for entry in words:
            match = re.match(r"(.*?)\n", entry)
            word = match.group(1).strip() if match else "Не найдено"
            st.markdown(f"- **{word}**")
        if st.button("🔁 Начать заново"):
            st.session_state["screen"] = "main"
            st.rerun()

# --- Нижняя плашка ---
def footer():
    st.markdown("---", unsafe_allow_html=True)
    footer_html = """
    <div style="display: flex; align-items: center; gap: 15px; padding: 10px 0;">
        <img src="lion.png" alt="lion" width="60" style="border-radius: 12px;" />
        <div style="font-style: italic; font-size: 18px; color: #e63946;">
            С любовью для львёнка ❤️
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# --- Инициализация данных ---
def initialize():
    if "words" not in st.session_state:
        md_path = Path("words.md")
        if not md_path.exists():
            st.error("Файл words.md не найден.")
            return
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        st.session_state["words"] = parse_words(content)
    if "screen" not in st.session_state:
        st.session_state["screen"] = "main"
    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0

# --- Основной запуск ---
def main():
    initialize()
    if st.session_state["screen"] == "main":
        main_screen()
    elif st.session_state["screen"] == "study":
        study_screen()
    footer()

if __name__ == "__main__":
    main()
