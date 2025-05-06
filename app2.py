import streamlit as st
import random
import json
import os

# ---------- Настройки темы ----------
def apply_theme():
    if st.session_state.get("dark_mode", False):
        st.markdown(\"""
            <style>
                body, .main, .block-container {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                .stButton button {
                    background-color: #333;
                    color: white;
                }
            </style>
        \""", unsafe_allow_html=True)
    else:
        st.markdown(\"""
            <style>
                body, .main, .block-container {
                    background-color: #FDF6EC;
                    color: #000000;
                }
            </style>
        \""", unsafe_allow_html=True)

# ---------- Загрузка данных ----------
def load_words():
    with open("quiz.md", "r", encoding="utf-8") as f:
        content = f.read()
    entries = content.split("## 🔤 ")[1:]
    return [entry.strip() for entry in entries]

def save_user_data():
    data = {}
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    user = st.session_state.get("current_user", "lion")
    if user not in data:
        data[user] = {"hard_words": [], "viewed_words": []}

    current_word = st.session_state["shuffled_words"][st.session_state["current_index"]]
    if current_word not in data[user]["viewed_words"]:
        data[user]["viewed_words"].append(current_word)

    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def mark_word_as_hard():
    data = {}
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    user = st.session_state.get("current_user", "lion")
    if user not in data:
        data[user] = {"hard_words": [], "viewed_words": []}

    current_word = st.session_state["shuffled_words"][st.session_state["current_index"]]
    if current_word not in data[user]["hard_words"]:
        data[user]["hard_words"].append(current_word)

    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Инициализация ----------
if "words" not in st.session_state:
    st.session_state["words"] = load_words()

if "screen" not in st.session_state:
    st.session_state["screen"] = "main"

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

if "current_user" not in st.session_state:
    st.session_state["current_user"] = "lion"

apply_theme()

# ---------- Главный экран ----------
def main_screen():
    st.title("📚 Учим английские слова")

    col_user, col_theme = st.columns([1, 1])

    with col_user:
        if st.button("🦁" if st.session_state["current_user"] == "lion" else "🦈"):
            st.session_state["current_user"] = "shark" if st.session_state["current_user"] == "lion" else "lion"
            st.rerun()

    with col_theme:
        if st.button("🌙" if not st.session_state["dark_mode"] else "☀️"):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()

    st.markdown("### Сколько слов учить?")
    col1, col2, col3 = st.columns(3)
    for count, col in zip([20, 30, 50], [col1, col2, col3]):
        with col:
            if st.button(f"{count} слов", use_container_width=True):
                st.session_state["word_count_choice"] = count
                st.session_state["screen"] = "study"
                st.session_state["current_index"] = 0
                st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=count)
                st.rerun()

# ---------- Экран изучения ----------
def study_screen():
    idx = st.session_state["current_index"]
    words = st.session_state["shuffled_words"]

    st.markdown(f"### 👤 Пользователь: {'🦁' if st.session_state['current_user'] == 'lion' else '🦈'}")

    st.markdown(f"#### Слово {idx + 1} из {len(words)}")
    st.markdown(f"---\\n{words[idx]}\\n---", unsafe_allow_html=True)

    save_user_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("↩️ На главный экран"):
            st.session_state["screen"] = "main"
            st.rerun()
    with col2:
        if st.button("🤔 Я не знаю"):
            mark_word_as_hard()
            st.success("Добавлено в список трудных слов")
    with col3:
        if st.button("➡️ Вперед"):
            if idx + 1 < len(words):
                st.session_state["current_index"] += 1
                st.rerun()
            else:
                st.session_state["screen"] = "finished"
                st.rerun()

# ---------- Финальный экран ----------
def finished_screen():
    st.success("🎉 Вы просмотрели все слова!")
    st.markdown("### Вот они:")

    for word in st.session_state["shuffled_words"]:
        st.markdown(f"- {word.splitlines()[0]}")

    if st.button("↩️ На главный экран"):
        st.session_state["screen"] = "main"
        st.rerun()

# ---------- Запуск ----------
if st.session_state["screen"] == "main":
    main_screen()
elif st.session_state["screen"] == "study":
    study_screen()
elif st.session_state["screen"] == "finished":
    finished_screen()

# ---------- Нижняя плашка ----------
st.markdown("---")
st.image("lion.png", width=50)
st.markdown("_С любовью для львёнка ❤️_", unsafe_allow_html=True)
