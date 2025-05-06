import streamlit as st
import random
import json
import os

# Инициализация сессии
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}

if "current_user" not in st.session_state:
    st.session_state["current_user"] = "lion"  # По умолчанию львенок

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True  # Темная тема по умолчанию

# Загружаем данные пользователей
def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            return json.load(file)
    return {}

# Сохраняем данные пользователей
def save_user_data():
    with open("user_data.json", "w") as file:
        json.dump(st.session_state["user_data"], file, indent=4)

# Загружаем данные для текущего пользователя
def get_user_data():
    return st.session_state["user_data"].get(st.session_state["current_user"], {"viewed_words": [], "hard_words": []})

# Обновляем данные для текущего пользователя
def update_user_data(viewed_words, hard_words):
    user_data = get_user_data()
    user_data["viewed_words"] = viewed_words
    user_data["hard_words"] = hard_words
    st.session_state["user_data"][st.session_state["current_user"]] = user_data
    save_user_data()

# Переключение темы
def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    if st.session_state["dark_mode"]:
        st.markdown(
            """
            <style>
            body {
                background-color: #1E1E1E;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #FFF8E1;  /* Цвет топленого молока */
                color: black;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Главный экран
def main_screen():
    st.title("📚 Учим английские слова")

    # Переключение пользователей
    user_icon = "🦁" if st.session_state["current_user"] == "lion" else "🦈"
    if st.button(f"Переключить пользователя: {user_icon}"):
        st.session_state["current_user"] = "lion" if st.session_state["current_user"] == "shark" else "shark"
        st.session_state["shuffled_words"] = []
        st.session_state["current_index"] = 0
        st.session_state["hard_words"] = []
        st.session_state["viewed_words"] = []
        st.session_state["rerun_theme"] = False
        st.rerun()

    # Иконка текущего пользователя
    st.markdown(f"### Текущий пользователь: {user_icon}")

    # Кнопка для переключения темы
    theme_icon = "☀️" if st.session_state["dark_mode"] else "🌙"
    if st.button(f"Переключить тему: {theme_icon}"):
        toggle_theme()
        st.rerun()

    # Выбор количества слов
    st.markdown("### Сколько слов учить?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("20 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 20
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=20)
            st.rerun()
    with col2:
        if st.button("30 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 30
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=30)
            st.rerun()
    with col3:
        if st.button("50 слов", use_container_width=True):
            st.session_state["word_count_choice"] = 50
            st.session_state["screen"] = "study"
            st.session_state["current_index"] = 0
            st.session_state["shuffled_words"] = random.sample(st.session_state["words"], k=50)
            st.rerun()

# Страница изучения слов
def study_screen():
    current_user_data = get_user_data()
    word_count = len(st.session_state["shuffled_words"])
    current_word = st.session_state["shuffled_words"][st.session_state["current_index"]]

    # Отображение текущего слова
    st.markdown(f"### {current_word}")
    
    # Кнопка "Я не знаю"
    if st.button("Я не знаю это слово"):
        current_user_data["hard_words"].append(current_word)
        update_user_data(current_user_data["viewed_words"], current_user_data["hard_words"])

    # Переход к следующему слову
    if st.button("Следующее слово"):
        if st.session_state["current_index"] < word_count - 1:
            st.session_state["current_index"] += 1
        else:
            st.session_state["screen"] = "review"
            st.session_state["current_index"] = 0
            st.rerun()

    # Прогресс
    progress = st.session_state["current_index"] + 1
    st.progress(progress / word_count)
    st.write(f"Прогресс: {progress}/{word_count}")

# Страница с трудными словами
def review_screen():
    current_user_data = get_user_data()
    hard_words = current_user_data["hard_words"]
    
    if hard_words:
        st.markdown("### Трудные слова")
        for word in hard_words:
            st.markdown(f"- {word}")
    else:
        st.markdown("Нет трудных слов!")

    if st.button("Вернуться на главный экран"):
        st.session_state["screen"] = "main"
        st.rerun()

# Основная логика переключения между экранами
def app():
    if "screen" not in st.session_state:
        st.session_state["screen"] = "main"

    if st.session_state["screen"] == "main":
        main_screen()
    elif st.session_state["screen"] == "study":
        study_screen()
    elif st.session_state["screen"] == "review":
        review_screen()

# Загрузка данных и запуск приложения
if __name__ == "__main__":
    st.session_state["user_data"] = load_user_data()
    app()
