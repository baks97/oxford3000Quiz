import streamlit as st
import time
import random

# Загружаем и парсим данные
def parse_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    words = []
    word = {}

    for line in lines:
        line = line.strip()

        if line.startswith("## 🔤"):
            if word:
                words.append(word)
            word = {'word': line[3:].strip()}  # Сохраняем слово, удаляя "## 🔤"
        elif line.startswith("**//"):
            word['transcription'] = line[2:-2]  # Убираем лишние символы вокруг транскрипции
        elif line.startswith("*"):
            word['part_of_speech'] = line[1:-1].strip()  # Часть речи
        elif line.startswith("### 📘 Oxford"):
            word['meaning'] = line
        elif line.startswith("### 🌍 Переводы (Cambridge)"):
            word['translation'] = line
        elif line.startswith("### 🧾 Примеры"):
            word['examples'] = line

    if word:
        words.append(word)  # Добавляем последнее слово

    return words

# Инициализация сессии
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'show' not in st.session_state:
    st.session_state.show = False

# Настройки и выбор количества слов
words_all = parse_md_file("quiz.md")
words_to_show = words_all[:7]  # Пример ограничения на 7 слов, можно менять по желанию

# Логика отображения для каждого слова
word = words_to_show[st.session_state.index]
st.write(f"Слово: {word['word']}")
st.write(f"Транскрипция: {word['transcription']}")
st.write(f"Часть речи: {word['part_of_speech']}")

# Кнопка для показа/скрытия значения
if st.button("Показать/Скрыть значение"):
    st.session_state.show = not st.session_state.show
    if st.session_state.show:
        st.write(f"Значение: {word['meaning']}")
        st.write(f"Перевод: {word['translation']}")
        st.write(f"Примеры: {word['examples']}")

# Кнопки для правильных/неправильных ответов
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("✅ Правильно"):
        st.session_state.answers.append((word['word'], True))

with col2:
    if st.button("❌ Неправильно"):
        st.session_state.answers.append((word['word'], False))

# Логика перехода к следующему слову или завершению квиза
if st.session_state.index + 1 < len(words_to_show):
    st.session_state.index += 1
else:
    st.session_state.page = "result"
    st.write("Квиз завершен")

# Переход в начало
if st.session_state.page == "result":
    st.write("Результаты квиза")
