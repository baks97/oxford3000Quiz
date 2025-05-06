import streamlit as st
import random
import re
from pathlib import Path

# Функция для парсинга слов из файла
def parse_words(md_text):
    entries = md_text.split("## 🔤 ")
    words = [entry.strip() for entry in entries if entry.strip()]
    return words

# Главная страница
def main_screen():
    st.title("Учить слова 📚")
    if st.button("🚀 Начать учить слова"):
        st.session_state["screen"] = "study"
        st.session_state["current_index"] = 0
        st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=50)
        st.rerun()

# Страница изучения слов
def study_screen():
    index = st.session_state["current_index"]
    words = st.session_state["shuffled_words"]

    if index < len(words):
        word_md = "## 🔤 " + words[index]
        with st.container(border=True):
            st.markdown(word_md, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➡️ Вперёд"):
                st.session_state["current_index"] += 1
                st.rerun()
        with col2:
            if st.button("🏠 На главный экран"):
                st.session_state["screen"] = "main"
                st.rerun()
    else:
        st.subheader("🎉 Вы выучили все 50 слов!")
        for entry in words:
            match = re.match(r"(.*?)\n", entry)
            word = match.group(1).strip() if match else "Не найдено"
            st.markdown(f"- **{word}**")

        if st.button("🔁 Начать заново"):
            st.session_state["screen"] = "main"
            st.rerun()

# Нижняя плашка с изображением и подписью
def footer():
    st.markdown("---")
    cols = st.columns([1, 8])
    with cols[0]:
        st.image("lion.png", width=45)
    with cols[1]:
        st.markdown("<p style='text-align: center; font-style: italic;'>с любовью от львёнка ❤️</p>", unsafe_allow_html=True)

# Инициализация
def initialize():
    if "screen" not in st.session_state:
        st.session_state["screen"] = "main"
    if "words" not in st.session_state:
        md_path = Path("words.md")
        if not md_path.exists():
            st.error("Файл words.md не найден.")
            return
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        st.session_state["words"] = parse_words(content)

# Основная логика
def main():
    # Надежная инициализация
    if "words" not in st.session_state:
        md_path = Path("quiz.md")
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

    if st.session_state["screen"] == "main":
        main_screen()
    elif st.session_state["screen"] == "study":
        study_screen()

    footer()

if __name__ == "__main__":
    main()
