import streamlit as st
import random
import json
import os

# Загрузка данных о пользователях из файла
def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {"lion": {"hard_words": [], "viewed_words": []},
                "shark": {"hard_words": [], "viewed_words": []}}

# Сохранение данных о пользователе в файл
def save_user_data(data):
    with open("user_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Главная страница
def main_screen():
    st.title("📚 Учим английские слова")

    # Переключение между львенком и акуленком
    if "user" not in st.session_state:
        st.session_state["user"] = "lion"  # по умолчанию львенок

    user_icon = "🦁" if st.session_state["user"] == "lion" else "🦈"

    # Кнопка для смены пользователя
    if st.button(f"Переключиться на {user_icon}"):
        st.session_state["user"] = "shark" if st.session_state["user"] == "lion" else "lion"
        st.experimental_rerun()  # Перезапуск страницы, чтобы применить изменения

    # Отображение значка текущего пользователя
    st.markdown(f"**Активный пользователь:** {user_icon}")

    # Выбор количества слов для изучения
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

# Экран изучения слов
def study_screen():
    user = st.session_state["user"]
    word = st.session_state["shuffled_words"][st.session_state["current_index"]]

    # Отображение карточки со словом
    st.markdown(f"### {word}")
    
    # Кнопки для перехода вперед и на главный экран
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤔 Я не знаю", use_container_width=True):
            # Добавляем слово в список трудных слов текущего пользователя
            user_data = load_user_data()
            if word not in user_data[user]["hard_words"]:
                user_data[user]["hard_words"].append(word)
            save_user_data(user_data)
            st.session_state["current_index"] += 1
            st.experimental_rerun()

    with col2:
        if st.button("➡️ Вперед", use_container_width=True):
            if st.session_state["current_index"] < len(st.session_state["shuffled_words"]) - 1:
                st.session_state["current_index"] += 1
                st.experimental_rerun()

    with col3:
        if st.button("🏠 На главный экран", use_container_width=True):
            st.session_state["screen"] = "main"
            st.experimental_rerun()

# Логика отображения экрана
if "screen" not in st.session_state:
    st.session_state["screen"] = "main"  # по умолчанию главный экран

if st.session_state["screen"] == "main":
    main_screen()
elif st.session_state["screen"] == "study":
    study_screen()
