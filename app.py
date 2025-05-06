import streamlit as st
import random
import time

# В начале скрипта
if "needs_rerun" in st.session_state and st.session_state.needs_rerun:
    st.session_state.needs_rerun = False
    st.rerun()

MD_FILE = "quiz.md"

st.set_page_config(page_title="🧠 Английский квиз", layout="centered")

st.set_page_config(page_title="Английский квиз", layout="wide")
st.title("🧠 Английский квиз по словам")
st.markdown("_by Львенок_")
st.image("lion.png", width=100)


st.set_page_config(page_title="🧠 Английский квиз", layout="centered")

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
if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "view_all" not in st.session_state:
    st.session_state.view_all = False

st.title("🧠 Английский квиз по словам")

if st.session_state.page == "start":
    st.subheader("Выберите количество слов:")

    col1, col2, col3, col4 = st.columns(4)
    for count, col in zip([7, 15, 20, 25], [col1, col2, col3, col4]):
        with col:
            if st.button(f"{count} слов"):
                st.session_state.words = random.sample(parse_md_file(MD_FILE), k=count)
                st.session_state.index = 0
                st.session_state.view_all = False
                st.session_state.page = "quiz"
                st.session_state.needs_rerun = True

    st.markdown(" ")
    st.write("Или:")
    if st.button("📂 Показать весь файл"):
        all_words = parse_md_file(MD_FILE)
        st.session_state.words = random.sample(all_words, k=len(all_words))
        st.session_state.index = 0
        st.session_state.view_all = True
        st.session_state.page = "quiz"
        st.session_state.needs_rerun = True
elif st.session_state.page == "quiz":
    words = st.session_state.words
    i = st.session_state.index

    word = words[i]
    st.markdown(f"### {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(f"*{word['pos']}*")
    st.markdown(word['examples'])
    st.markdown(word['rest'])
    st.markdown(word['cambridge'])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Предыдущее") and i > 0:
            st.session_state.index -= 1
    with col2:
        if st.button("➡ Следующее") and i < len(words) - 1:
            st.session_state.index += 1

    if st.session_state.view_all and st.session_state.index == len(words) - 1:
        st.markdown(" ")
        if st.button("🔁 Начать заново"):
            st.session_state.page = "start"
            st.session_state.needs_rerun = True
