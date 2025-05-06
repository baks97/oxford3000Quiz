import streamlit as st
import random
import json
import os

# Загружаем слова из файла words.md
def load_words_from_file():
    with open("words.md", "r", encoding="utf-8") as f:
        words = f.read().splitlines()
    return words

# Инициализация сессии
if "words" not in st.session_state:
    st.session_state["words"] = load_words_from_file()
if "screen" not in st.session_state:
    st.session_state["screen"] = "main"
if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0
if "shuffled_words" not in st.session_state:
    st.session_state["shuffled_words"] = []
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "user" not in st.session_state:
    st.session_state["user"] = "lion"  # default user

# Функция для загрузки или сохранения данных пользователя
def load_user_data():
    if not os.path.exists("user_data.json"):
        return {}
    with open("user_data.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # если файл пустой или поврежден, возвращаем пустой словарь

def save_user_data(user_data):
    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

user_data = load_user_data()

# Функция для переключения темы
def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]

# Главный экран
def main_screen():
    st.title("📚 Учим английские слова")

    # Переключение темы
    theme_button = "🌙 Переключить тему" if not st.session_state["dark_mode"] else "☀️ Переключить тему"
    if st.button(theme_button):
        toggle_theme()
        st.rerun()

    # Переключение пользователя
    user_button = "🦁 Львенок" if st.session_state["user"] == "lion" else "🦈 Акуленок"
    if st.button(user_button):
        st.session_state["user"] = "shark" if st.session_state["user"] == "lion" else "lion"
        st.rerun()

    # Выбор количества слов для изучения
    st.markdown("### Сколько слов учить?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("20 слов", use_container_width=True):
            start_study(20)
    with col2:
        if st.button("30 слов", use_container_width=True):
            start_study(30)
    with col3:
        if st.button("50 слов", use_container_width=True):
            start_study(50)

    # Плашка с картинкой
    st.markdown(f'<div style="text-align: center;"><img src="lion.png" width="100"/><p>С любовью для львёнка ❤️</p></div>', unsafe_allow_html=True)

# Функция начала обучения
def start_study(word_count):
    st.session_state["screen"] = "study"
    st.session_state["current_index"] = 0
    st.session_state["word_count_choice"] = word_count
    st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=word_count)
    st.session_state["rerun_theme"] = False
    st.rerun()

# Страница изучения слов
def study_screen():
    words = st.session_state["shuffled_words"]
    index = st.session_state["current_index"]

    if index < len(words):
        current_word = words[index]
        st.subheader(f"Слово {index + 1} из {len(words)}: {current_word}")

        # Кнопки управления
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Я не знаю"):
                add_to_hard_words(current_word)
        with col2:
            if st.button("Вперед"):
                st.session_state["current_index"] += 1
                st.rerun()
        with col3:
            if st.button("На главный экран"):
                st.session_state["screen"] = "main"
                st.session_state["current_index"] = 0
                st.session_state["shuffled_words"] = []
                st.rerun()

        # Значок активного пользователя
        active_user_icon = "🦁 Львенок" if st.session_state["user"] == "lion" else "🦈 Акуленок"
        st.markdown(f"### Активный пользователь: {active_user_icon}")
    else:
        show_results_screen()

# Функция для добавления трудного слова в список
def add_to_hard_words(word):
    user = st.session_state["user"]
    if user not in user_data:
        user_data[user] = {"hard_words": [], "viewed_words": []}
    
    if word not in user_data[user]["hard_words"]:
        user_data[user]["hard_words"].append(word)
    
    # Сохраняем данные
    save_user_data(user_data)

# Страница с результатами
def show_results_screen():
    st.header("Вы изучили следующие слова:")
    user = st.session_state["user"]
    words_learned = user_data.get(user, {}).get("viewed_words", [])
    if words_learned:
        st.write(", ".join(words_learned))
    else:
        st.write("Еще не изучены слова.")
    
    # Переключение обратно на главный экран
    if st.button("На главный экран"):
        st.session_state["screen"] = "main"
        st.session_state["current_index"] = 0
        st.session_state["shuffled_words"] = []
        st.rerun()

# Отображение экрана в зависимости от состояния
if st.session_state["screen"] == "main":
    main_screen()
elif st.session_state["screen"] == "study":
    study_screen()
else:
    st.error("Неизвестный экран!")
