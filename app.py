import streamlit as st
import random

def parse_md_file(filename):
    with open(filename, encoding="utf-8") as f:
        content = f.read()
    entries = content.split("## 🔤 ")[1:]
    words = []
    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue
        word = lines[0].strip()
        transcription = lines[1].strip()
        pos = lines[2].strip()
        examples_block = ""
        cambridge_block = ""
        rest_block = ""
        current_block = None
        for line in lines[3:]:
            if line.startswith("### 🧾"):
                current_block = "examples"
                examples_block += line + "\n"
            elif line.startswith("### 🌍"):
                current_block = "cambridge"
                cambridge_block += line + "\n"
            elif line.startswith("### 📘") or line.startswith("### 📌"):
                current_block = "rest"
                rest_block += line + "\n"
            elif current_block:
                if current_block == "examples":
                    examples_block += line + "\n"
                elif current_block == "cambridge":
                    cambridge_block += line + "\n"
                elif current_block == "rest":
                    rest_block += line + "\n"
        words.append({
            "word": word,
            "transcription": transcription,
            "pos": pos,
            "examples": examples_block.strip(),
            "cambridge": cambridge_block.strip(),
            "rest": rest_block.strip()
        })
    return words

# Инициализация состояния
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
    st.write("Выберите режим:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Учить слова"):
            st.session_state.words = random.sample(words_all, 50)
            st.session_state.page = "learn"
            st.session_state.index = 0
    with col2:
        if st.button("📝 Пройти тест"):
            st.session_state.page = "select_test"

# Выбор количества слов
elif st.session_state.page == "select_test":
    st.write("Выберите количество слов для теста:")
    for count in [7, 15, 20, 25]:
        if st.button(f"{count} слов"):
            st.session_state.words = random.sample(words_all, count)
            st.session_state.index = 0
            st.session_state.stats = {}
            st.session_state.page = "test"
            st.session_state.show_card = False

# Режим "Учить слова"
elif st.session_state.page == "learn":
    word = st.session_state.words[st.session_state.index]
    st.markdown(f"### {word['word']}")
    st.write(f"**Транскрипция:** {word['transcription']}")
    st.write(f"**Часть речи:** {word['pos']}")
    st.markdown(f"{word['examples']}")
    st.markdown(f"{word['cambridge']}")
    st.markdown(f"{word['rest']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀️ Назад") and st.session_state.index > 0:
            st.session_state.index -= 1
    with col2:
        st.button("🏠 Главный экран", on_click=lambda: st.session_state.update({"page": "main"}))
    with col3:
        if st.button("▶️ Далее") and st.session_state.index < len(st.session_state.words) - 1:
            st.session_state.index += 1

# Режим "Тест"
elif st.session_state.page == "test":
    if st.session_state.index >= len(st.session_state.words):
        st.write("✅ Тест завершён!")
        correct = sum(1 for res in st.session_state.stats.values() if res == True)
        incorrect = sum(1 for res in st.session_state.stats.values() if res == False)
        st.write(f"**Правильно:** {correct}")
        st.write(f"**Неправильно:** {incorrect}")
        st.write("Ответы:")
        for word, result in st.session_state.stats.items():
            st.write(f"{word}: {'✅' if result else '❌'}")
        if st.button("🏠 На главный экран"):
            st.session_state.page = "main"
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
