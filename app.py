import streamlit as st
import random
import time
import json

MD_FILE = "quiz.md"

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    words = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("## 🔤 "):
            word_entry = {
                "word": lines[i][5:].strip(),
                "transcription": lines[i+1] if i+1 < len(lines) else "",
                "part_of_speech": lines[i+2] if i+2 < len(lines) else "",
                "examples": "",
                "extra": "",
            }

            # Поиск блока ### 🧾
            for j in range(i+3, len(lines)):
                if lines[j].startswith("### 🧾"):
                    examples_start = j
                    break
            else:
                examples_start = None

            # Поиск следующего слова
            for j in range(i+1, len(lines)):
                if lines[j].startswith("## 🔤 "):
                    next_word_start = j
                    break
            else:
                next_word_start = len(lines)

            if examples_start is not None:
                word_entry["examples"] = "\n".join(lines[examples_start:next_word_start])
                word_entry["extra"] = "\n".join(lines[i+3:examples_start])
            else:
                word_entry["examples"] = ""
                word_entry["extra"] = "\n".join(lines[i+3:next_word_start])

            words.append(word_entry)
            i = next_word_start
        else:
            i += 1
    return words

# Загрузка и сохранение статистики
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# Инициализация состояний
if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "show" not in st.session_state:
    st.session_state.show = False
if "stats" not in st.session_state:
    st.session_state.stats = load_stats()

# Начальный экран
if st.session_state.page == "start":
st.title("🧠 Английский квиз по словам")

if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "show" not in st.session_state:
    st.session_state.show = False
if "answers" not in st.session_state:
    st.session_state.answers = []
if "stats" not in st.session_state:
    st.session_state.stats = {}
if "seed" not in st.session_state:
    st.session_state.seed = None

if st.session_state.page == "start":
    st.subheader("Выберите количество слов для квиза:")

    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        with col:
            if st.button(f"{n} слов"):
                st.session_state.seed = random.randint(1, 999999)
                random.seed(st.session_state.seed)
                all_words = parse_md_file(MD_FILE)
                st.session_state.words = random.sample(all_words, n)
                st.session_state.page = "quiz"
                st.session_state.index = 0
                st.session_state.answers = []
                st.session_state.show = False
                st.experimental_rerun()

    st.write("📂 Или показать весь список слов")
    if st.button("Показать весь файл"):
        st.session_state.page = "full"
        st.experimental_rerun()

    st.write("Или:")
    if st.button("📂 Показать весь файл"):
        st.session_state.words = sorted(parse_md_file(MD_FILE), key=lambda x: x["word"].lower())
        st.session_state.page = "all"

    if st.button("📈 Показать статистику"):
        st.session_state.page = "stats"

# Экран статистики
elif st.session_state.page == "stats":
    st.title("📊 Статистика")
    stats = st.session_state.stats
    for word, record in stats.items():
        st.markdown(f"**{word}** — ✅ {record.get('right', 0)}, ❌ {record.get('wrong', 0)}")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"

# Экран всего файла
elif st.session_state.page == "all":
    st.title("📚 Все слова")
    for word in st.session_state.words:
        st.markdown(f"### {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['part_of_speech'])
        st.markdown(word['examples'])
        st.markdown(word['cambridge'])

    if st.button("🔙 Назад"):
        st.session_state.page = "start"

# Основной квиз
elif st.session_state.page == "quiz":
    if st.session_state.index >= len(st.session_state.words):
        st.title("✅ Результаты")
        for word, correct in st.session_state.answers:
            color = "green" if correct else "red"
            st.markdown(f"<span style='color:{color}'>{word}</span>", unsafe_allow_html=True)
        if st.button("🔁 Начать заново"):
            st.session_state.page = "start"
    else:
        word = st.session_state.words[st.session_state.index]
        st.markdown(f"### {word['word']}")
        st.markdown(word["transcription"])
        st.markdown(word["part_of_speech"])

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("❌ Неправильно"):
                st.session_state.answers.append((word['word'], False))
                if word['word'] not in st.session_state.stats:
                    st.session_state.stats[word['word']] = {"right": 0, "wrong": 0}
                st.session_state.stats[word['word']]["wrong"] += 1
                save_stats(st.session_state.stats)
                st.session_state.index += 1
                st.session_state.show = False

        with col2:
            if st.button("👁 Показать значение"):
                st.session_state.show = not st.session_state.show

        with col3:
            if st.button("✅ Правильно"):
                st.session_state.answers.append((word['word'], True))
                if word['word'] not in st.session_state.stats:
                    st.session_state.stats[word['word']] = {"right": 0, "wrong": 0}
                st.session_state.stats[word['word']]["right"] += 1
                save_stats(st.session_state.stats)
                st.session_state.index += 1
                st.session_state.show = False

        if st.session_state.show:
            st.markdown(word["examples"])
            st.markdown(word["cambridge"])
