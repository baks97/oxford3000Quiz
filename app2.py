import streamlit as st
import random
import re
from pathlib import Path
import base64

# --- Настройки страницы ---
st.set_page_config(page_title="Учить слова", page_icon="📚", layout="centered")

# --- Темы ---
def apply_theme():
    if st.session_state.get("dark_mode", False):
        # Тёмная тема
        st.markdown("""
            <style>
                body, .stApp { background-color: #121212; color: #f1f1f1; }
                .word-card { background-color: #1e1e1e; color: #f1f1f1; }
                .footer-text { color: #ffcccc; }
            </style>
        """, unsafe_allow_html=True)
    else:
        # Светлая тема (цвет топленого молока)
        st.markdown("""
            <style>
                body, .stApp { background-color: #f5e0c3; color: black; }
                .word-card { background-color: #ffffff; color: black; }
                .footer-text { color: #e63946; }
            </style>
        """, unsafe_allow_html=True)

# --- Парсинг слов ---
def parse_words(md_text):
    entries = md_text.split("## 🔤 ")
    return [entry.strip() for entry in entries if entry.strip()]

# --- Главный экран ---
def main_screen():
    st.title("📚 Учим английские слова")

    # Переключатель темы
    new_theme = st.toggle("🌙 Темная тема", key="dark_mode")
    if new_theme != st.session_state.get("current_theme", None):
        st.session_state["current_theme"] = new_theme
        st.session_state["rerun_theme"] = True

    # Выбор количества слов
    st.markdown("### Сколько слов учить?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("20 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 20
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=20)
            st.session_state["rerun_theme"] = False
            st.rerun()
    with col2:
        if st.button("30 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 30
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=30)
            st.session_state["rerun_theme"] = False
            st.rerun()
    with col3:
        if st.button("50 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 50
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=50)
            st.session_state["rerun_theme"] = False
            st.rerun()

# --- Экран изучения слов ---
def study_screen():
    index = st.session_state["current_index"]
    words = st.session_state["shuffled_words"]

    if index < len(words):
        word_md = "## 🔤 " + words[index]

        st.markdown(f"""
            <div class="word-card" style="
                padding: 25px;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            ">
                {word_md}
            </div>
        """, unsafe_allow_html=True)

        st.progress((index + 1) / len(words))
        st.caption(f"Слово {index + 1} из {len(words)}")

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
        st.subheader("🎉 Вы выучили все слова!")
        st.markdown("### Вот они:")
        for entry in words:
            match = re.match(r"(.*?)\n", entry)
            word = match.group(1).strip() if match else "Не найдено"
            st.markdown(f"- **{word}**")
        if st.button("🔁 Начать заново"):
            st.session_state["screen"] = "main"
            st.rerun()

# --- Нижняя плашка с изображением ---
def footer():
    st.markdown("---", unsafe_allow_html=True)

    # Чтение и отображение изображения львёнка
    image_path = "lion.png"
    if Path(image_path).exists():
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()
        img_html = f'<img src="data:image/png;base64,{encoded}" width="60" style="border-radius:12px;" />'
    else:
        img_html = ""

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; padding: 10px 0;">
        {img_html}
        <div class="footer-text" style="font-style: italic; font-size: 18px;">
            С любовью для львёнка ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Инициализация ---
def initialize():
    if "words" not in st.session_state:
        md_path = Path("quiz.md")  # Поменяли на новый файл quiz.md
        if not md_path.exists():
            st.error("Файл quiz.md не найден.")
            return
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        st.session_state["words"] = parse_words(content)
    if "screen" not in st.session_state:
        st.session_state["screen"] = "main"
    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    if "word_count_choice" not in st.session_state:
        st.session_state["word_count_choice"] = 50
    if "rerun_theme" not in st.session_state:
        st.session_state["rerun_theme"] = False

# --- Основной запуск ---
def main():
    initialize()
    apply_theme()

    # Перезапуск после изменения темы
    if st.session_state.get("rerun_theme", False):
        st.session_state["rerun_theme"] = False
        st.rerun()

    if st.session_state["screen"] == "main":
        main_screen()
    elif st.session_state["screen"] == "study":
        study_screen()

    footer()

if __name__ == "__main__":
    main()
