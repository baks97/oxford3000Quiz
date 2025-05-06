import streamlit as st
import random
import re
from pathlib import Path

# ---------- Загрузка слов ----------
def load_words_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    raw_entries = re.split(r"\n##\s", content)[1:]
    words = []
    for entry in raw_entries:
        entry = "## " + entry.strip()
        word_match = re.search(r"##\s+(.+)", entry)
        word = word_match.group(1).strip() if word_match else "Unknown"
        words.append({"word": word, "content": entry})
    return words

# ---------- Инициализация session_state ----------
if "words" not in st.session_state:
    st.session_state.words = load_words_from_md("quiz.md")
if "screen" not in st.session_state:
    st.session_state.screen = "main"
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "shuffled_words" not in st.session_state:
    st.session_state.shuffled_words = []
if "word_count" not in st.session_state:
    st.session_state.word_count = 50
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------- Применение темы ----------
def apply_theme():
    if st.session_state.get("dark_mode", False):
        st.markdown("""
            <style>
                body, .stApp { background-color: #121212; color: #f1f1f1; }
                .word-card { background-color: #1e1e1e; color: #f1f1f1; }
                .footer-text { color: #ffcccc; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                body, .stApp { background-color: #f5e0c3; color: black; }
                .word-card { background-color: #ffffff; color: black; }
                .footer-text { color: #e63946; }
            </style>
        """, unsafe_allow_html=True)

apply_theme()

# ---------- Переключение темы ----------
def theme_switcher():
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("🌞" if not st.session_state.get("dark_mode", False) else "🌙"):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()

# ---------- Главный экран ----------
def main_screen():
    theme_switcher()
    st.markdown("<h1 style='text-align: center;'>Учить слова</h1>", unsafe_allow_html=True)

    st.write("Выбери количество слов:")
    cols = st.columns(3)
    for i, n in enumerate([20, 30, 50]):
        with cols[i]:
            if st.button(f"{n} слов"):
                st.session_state.word_count = n
                st.session_state.shuffled_words = random.sample(st.session_state.words, n)
                st.session_state.current_index = 0
                st.session_state.screen = "study"
                st.rerun()

    show_footer()

# ---------- Страница изучения ----------
def study_screen():
    idx = st.session_state.current_index
    total = st.session_state.word_count
    word_entry = st.session_state.shuffled_words[idx]

    st.markdown(f"""
        <div class='word-card' style='padding: 1.5em; border-radius: 1em; margin-bottom: 1em;'>
            {word_entry['content']}
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Вперёд"):
            if idx + 1 < total:
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.session_state.screen = "result"
                st.rerun()
    with col2:
        if st.button("🏠 На главный экран"):
            st.session_state.screen = "main"
            st.rerun()

    show_footer()

# ---------- Экран результата ----------
def result_screen():
    st.markdown("<h2>Поздравляю! Вот слова, которые ты выучил:</h2>", unsafe_allow_html=True)
    st.markdown("<ul>" + "".join(
        f"<li>{entry['word']}</li>" for entry in st.session_state.shuffled_words
    ) + "</ul>", unsafe_allow_html=True)

    if st.button("🏠 На главный экран"):
        st.session_state.screen = "main"
        st.rerun()

    show_footer()

# ---------- Нижняя плашка ----------
def show_footer():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; margin-top: 2em;'>
            <img src='data:image/png;base64,{}' width='60'>
            <span class='footer-text' style='margin-left: 1em; font-style: italic; font-size: 1.2em;'>с любовью для львёнка ❤️</span>
        </div>
    """.format(image_to_base64("lion.png")), unsafe_allow_html=True)

# ---------- Загрузка изображения львёнка ----------
def image_to_base64(image_path):
    import base64
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# ---------- Запуск нужного экрана ----------
if st.session_state.screen == "main":
    main_screen()
elif st.session_state.screen == "study":
    study_screen()
elif st.session_state.screen == "result":
    result_screen()
