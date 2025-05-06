import streamlit as st
import random

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.split("\n\n\n")  # разделение по пустым строкам
    words = []

    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue  # пропускаем неполные записи

        word = lines[0].strip()
        transcription = lines[1].strip()

        # Ищем строку, содержащую часть речи
        part_of_speech = ""
        for line in lines[2:]:
            if line.startswith("*") and line.endswith("*"):
                part_of_speech = line.strip("*").strip()
                break

        # Извлекаем блоки
        examples_block = ""
        meanings_block = ""
        translations_block = ""

        in_examples = False
        in_meanings = False
        in_translations = False

        for line in lines:
            if line.startswith("### 🧾"):
                in_examples = True
                in_meanings = False
                in_translations = False
                examples_block += line + "\n"
            elif line.startswith("### 📘"):
                in_examples = False
                in_meanings = True
                in_translations = False
                meanings_block += line + "\n"
            elif line.startswith("### 🌍"):
                in_examples = False
                in_meanings = False
                in_translations = True
                translations_block += line + "\n"
            elif in_examples:
                examples_block += line + "\n"
            elif in_meanings:
                meanings_block += line + "\n"
            elif in_translations:
                translations_block += line + "\n"

        words.append({
            "word": word,
            "transcription": transcription,
            "part_of_speech": part_of_speech,
            "examples": examples_block.strip(),
            "meanings": meanings_block.strip(),
            "translations": translations_block.strip()
        })

    return words

# Сессия
if 'page' not in st.session_state:
    st.session_state.page = 'main'
    st.session_state.words = []
    st.session_state.index = 0
    st.session_state.stats = {}
    st.session_state.test_mode = False
    st.session_state.show_card = False

# Заголовок
st.title("🧠 Английский квиз по словам")
words_all = parse_md_file("quiz.md")

# Главный экран
if st.session_state.page == 'main':
    st.markdown("<h3 style='text-align: center;'>Выберите режим:</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Учить слова", use_container_width=True):
            st.session_state.words = random.sample(words_all, 50)
            st.session_state.page = "learn"
            st.session_state.index = 0
    with col2:
        if st.button("📝 Пройти тест", use_container_width=True):
            st.session_state.page = "select_test"

# Выбор слов
elif st.session_state.page == "select_test":
    st.markdown("<h4 style='text-align: center;'>Выберите количество слов для теста:</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for count, col in zip([7, 15, 20, 25], [col1, col2, col3, col4]):
        with col:
            if st.button(f"{count} слов", use_container_width=True):
                st.session_state.words = random.sample(words_all, count)
                st.session_state.index = 0
                st.session_state.stats = {}
                st.session_state.page = "test"
                st.session_state.show_card = False

# Учить слова
elif st.session_state.page == "learn":
    word = st.session_state.words[st.session_state.index]
    st.markdown(f"### {word['word']}")
    st.write(f"**Транскрипция:** {word['transcription']}")
    st.write(f"**Часть речи:** {word['pos']}")
    st.markdown(f"{word['examples']}")
    st.markdown(f"{word['cambridge']}")
    st.markdown(f"{word['rest']}")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀️ Назад") and st.session_state.index > 0:
            st.session_state.index -= 1
    with col2:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.button("🏠 Главный экран", on_click=lambda: st.session_state.update({"page": "main"}))
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        if st.button("▶️ Далее") and st.session_state.index < len(st.session_state.words) - 1:
            st.session_state.index += 1

# Тест
elif st.session_state.page == "test":
    if st.session_state.index >= len(st.session_state.words):
        st.success("✅ Тест завершён!")
        correct = sum(1 for res in st.session_state.stats.values() if res)
        incorrect = sum(1 for res in st.session_state.stats.values() if not res)
        st.write(f"**Правильно:** {correct}")
        st.write(f"**Неправильно:** {incorrect}")
        st.write("Ответы:")
        for word, result in st.session_state.stats.items():
            st.write(f"{word}: {'✅' if result else '❌'}")
        st.button("🏠 На главный экран", on_click=lambda: st.session_state.update({"page": "main"}))
    else:
        word = st.session_state.words[st.session_state.index]
        st.markdown(f"### {word['word']}")
        st.write(f"**Транскрипция:** {word['transcription']}")
        st.write(f"**Часть речи:** {word['pos']}")

        if st.button("Показать карточку"):
            st.session_state.show_card = True

        if st.session_state.show_card:
            st.markdown(f"{word['examples']}")
            st.markdown(f"{word['cambridge']}")
            st.markdown(f"{word['rest']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Правильно"):
                st.session_state.stats[word['word']] = True
                st.session_state.index += 1
                st.session_state.show_card = False
        with col2:
            if st.button("❌ Неправильно"):
                st.session_state.stats[word['word']] = False
                st.session_state.index += 1
                st.session_state.show_card = False
        st.button("🏠 Главный экран", on_click=lambda: st.session_state.update({"page": "main"}))
        
# Надпись и изображение внизу главного экрана
if st.session_state.page == "main":
    st.markdown("<hr>", unsafe_allow_html=True)
    st.image("lion.png", use_column_width=True, caption="", output_format="auto")
    st.markdown("<p style='text-align: center; font-style: italic;'>с любовью от львёнка ❤️</p>", unsafe_allow_html=True)
else:
# Надпись внизу
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>с любовью от львёнка ❤️</p>", unsafe_allow_html=True)
