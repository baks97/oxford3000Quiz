import streamlit as st
import random

# Пример списка слов
words = [
    {"word": "abandon", "transcription": "/əˈbændən/", "part_of_speech": "verb", "definition": "to leave somebody", "examples": ["The baby had been abandoned by its mother."]},
    {"word": "abandoned", "transcription": "/əˈbændənd/", "part_of_speech": "adjective", "definition": "left and no longer wanted", "examples": ["An abandoned car."]},
    # Добавьте больше слов по вашему желанию
]

# Инициализация переменных
if "index" not in st.session_state:
    st.session_state.index = 0
if "show" not in st.session_state:
    st.session_state.show = False
if "answers" not in st.session_state:
    st.session_state.answers = []

# Выбор количества слов
words_to_show = st.radio("Выберите количество слов", (7, 15, 20, 25), index=1)

# Показать слово
word = words[st.session_state.index]

# Кнопки для выбора правильного/неправильного ответа
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("✅ Правильно"):
        # Здесь не обновляется статистика, просто идем к следующему слову
        st.session_state.index += 1
        st.session_state.show = False

with col3:
    if st.button("❌ Неправильно"):
        # Здесь тоже не обновляется статистика, просто идем к следующему слову
        st.session_state.index += 1
        st.session_state.show = False

# Кнопка "Показать значение"
if st.button("Показать значение"):
    st.session_state.show = not st.session_state.show

# Отображение информации о слове
st.write(f"Слово: {word['word']}")
st.write(f"Транскрипция: {word['transcription']}")
st.write(f"Часть речи: {word['part_of_speech']}")

if st.session_state.show:
    st.write(f"Значение: {word['definition']}")
    st.write(f"Примеры: {', '.join(word['examples'])}")
