import streamlit as st
import random
import time

# Чтение данных
def parse_md_file(filename):
    with open(filename, encoding="utf-8") as f:
        content = f.read()

    entries = content.split("## 🔤 ")[1:]
    words = []
    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue  # пропустить карточки с отсутствием обязательных строк

        word = lines[0].strip()
        transcription = lines[1].strip()
        pos = lines[2].strip()

        # Найти блоки
        examples_block = ""
        rest_block = ""
        cambridge_block = ""

        in_examples = False
        in_rest = False
        in_cambridge = False

        for line in lines[3:]:
            if line.startswith("### 🧾"):
                in_examples = True
                in_rest = in_cambridge = False
                examples_block += line + "\n"
            elif line.startswith("### 🌍"):
                in_cambridge = True
                in_examples = in_rest = False
                cambridge_block += line + "\n"
            elif line.startswith("### 📘") or line.startswith("### 📌"):
                in_rest = True
                in_examples = in_cambridge = False
                rest_block += line + "\n"
            elif line.startswith("## 🔤"):
                break
            else:
                if in_examples:
                    examples_block += line + "\n"
                elif in_rest:
                    rest_block += line + "\n"
                elif in_cambridge:
                    cambridge_block += line + "\n"

        words.append({
            "word": word,
            "transcription": transcription,
            "pos": pos,
            "examples": examples_block.strip(),
            "rest": rest_block.strip(),
            "cambridge": cambridge_block.strip()
        })

    return words

# Инициализация состояния
if 'page' not in st.session_state:
    st.session_state.page = 'main'
    st.session_state.words = []
    st.session_state.index = 0
    st.session_state.stats = {}
    st.session_state.test_mode = False
    st.session_state.view_all = False

# Заголовок
st.title("🧠 Английский квиз по словам")

# Чтение файла
MD_FILE = "quiz.md"
words_all = parse_md_file(MD_FILE)

# Главный экран
if st.session_state.page == 'main':
    st.write("Выберите режим:")

    # Выбор режима
    mode = st.selectbox("Выберите режим", ["Учить слова", "Проверка слов"])

    if mode == "Учить слова":
        st.session_state.words = random.sample(words_all, len(words_all))  # случайный порядок всех слов
        st.session_state.test_mode = False
        st.session_state.page = 'quiz'
    elif mode == "Проверка слов":
        st.session_state.test_mode = True
        st.session_state.page = 'test'

    st.write("Выберите количество слов для теста:")

    # Выбор количества слов для теста
    if st.button("7 слов"):
        st.session_state.words = random.sample(words_all, 7)
        st.session_state.index = 0
        st.session_state.page = "test"
    elif st.button("15 слов"):
        st.session_state.words = random.sample(words_all, 15)
        st.session_state.index = 0
        st.session_state.page = "test"
    elif st.button("20 слов"):
        st.session_state.words = random.sample(words_all, 20)
        st.session_state.index = 0
        st.session_state.page = "test"
    elif st.button("25 слов"):
        st.session_state.words = random.sample(words_all, 25)
        st.session_state.index = 0
        st.session_state.page = "test"

    # Кнопка для отображения всего файла
    if st.button("📂 Показать весь файл"):
        st.session_state.page = "all_words"
        st.session_state.view_all = True

# Тестирование слов
elif st.session_state.page == 'test':
    word = st.session_state.words[st.session_state.index]

    # Отображение текущего слова
    st.write(f"### {word['word']}")
    st.write(f"**Транскрипция:** {word['transcription']}")
    st.write(f"**Часть речи:** {word['pos']}")

    # Кнопка для отображения карточки
    if st.button("Показать карточку"):
        st.write(f"**Примеры:** {word['examples']}")
        st.write(f"**Перевод (Cambridge):** {word['cambridge']}")
        st.write(f"**Остальная информация:** {word['rest']}")

    # Кнопки для правильных и неправильных ответов
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Правильно"):
            st.session_state.stats[word['word']] = {"right": 1, "wrong": 0}
            st.session_state.index += 1
    with col2:
        if st.button("❌ Неправильно"):
            st.session_state.stats[word['word']] = {"right": 0, "wrong": 1}
            st.session_state.index += 1

    # Кнопки для переключения слов
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀️ Предыдущее"):
            st.session_state.index -= 1
    with col2:
        if st.button("🏠 Главный экран"):
            st.session_state.page = "main"
    with col3:
        if st.button("▶️ Следующее"):
            st.session_state.index += 1

    # Окончание теста
    if st.session_state.index >= len(st.session_state.words):
        st.write(f"Тест завершен! Результат:")
        correct = sum([1 for stat in st.session_state.stats.values() if stat["right"] == 1])
        wrong = sum([1 for stat in st.session_state.stats.values() if stat["wrong"] == 1])
        st.write(f"Правильных ответов: {correct}")
        st.write(f"Неправильных ответов: {wrong}")
        st.write("Ваши ответы:")
        for word, stat in st.session_state.stats.items():
            st.write(f"{word}: {'Правильно' if stat['right'] == 1 else 'Неправильно'}")

# Просмотр всего файла
elif st.session_state.page == 'all_words':
    st.write("Все слова:")
    for word in sorted(words_all, key=lambda x: x['word']):
        st.write(f"### {word['word']}")
        st.write(f"**Транскрипция:** {word['transcription']}")
        st.write(f"**Часть речи:** {word['pos']}")
        st.write(f"**Примеры:** {word['examples']}")
        st.write(f"**Перевод (Cambridge):** {word['cambridge']}")
        st.write(f"**Остальная информация:** {word['rest']}")
