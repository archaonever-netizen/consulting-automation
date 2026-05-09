import streamlit as st
from groq import Groq

# ---------- НАСТРОЙКА СТРАНИЦЫ ----------
st.set_page_config(page_title="Консалтинг Презентация", layout="wide")

# ---------- CSS ДЛЯ ПРЕЗЕНТАЦИИ ----------
st.markdown("""
<style>
    .presentation-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 30px 25px 25px 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 6px solid #1E3A8A;
    }
    .presentation-card h2 {
        color: #1E3A8A;
        font-size: 2em;
        margin-top: 0;
        border-bottom: 2px solid #1E3A8A30;
        padding-bottom: 10px;
    }
    .presentation-card h3 {
        color: #2563EB;
        font-size: 1.4em;
    }
    .presentation-card p, .presentation-card li {
        font-size: 1.1em;
        line-height: 1.6;
        color: #1F2937;
    }
    .presentation-card ul {
        padding-left: 20px;
    }
    .presentation-card .highlight {
        background: #DBEAFE;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        font-weight: bold;
    }
    .slide-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    .slide-icon {
        font-size: 2.5rem;
    }
    .metrics-box {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 10px 15px;
        display: inline-block;
        margin: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------- ЗАГОЛОВОК ----------
st.title("🌟 Система консалтинговой компании")
st.markdown("### Ваш персональный ИИ-консультант с продающими презентациями", unsafe_allow_html=True)

# ---------- КЛЮЧ API ----------
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

st.sidebar.text_input(
    "🔑 Введите Groq API Key",
    type="password",
    key="api_key_input",
    on_change=lambda: st.session_state.update(groq_api_key=st.session_state.api_key_input or "")
)

client = None
if st.session_state.groq_api_key:
    client = Groq(api_key=st.session_state.groq_api_key)

# ---------- ДАННЫЕ СЕССИИ ----------
if "lead_data" not in st.session_state:
    st.session_state.lead_data = {}

# ---------- ФУНКЦИЯ ЗАПРОСА К LLM ----------
def ask_agent(system_prompt, user_message, model="llama-3.3-70b-versatile"):
    if not client:
        st.error("Введите API‑ключ в боковой панели.")
        return None
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
        max_tokens=2048
    )
    return response.choices[0].message.content

# ---------- ФОРМАТИРОВАНИЕ ВЫВОДА КАК ПРЕЗЕНТАЦИЯ ----------
def display_presentation(title, content, icon=""):
    """Оборачивает ответ агента в красивую карточку."""
    if not content:
        return
    # Заменяем Markdown на HTML с сохранением структуры
    html_content = content.replace("\n", "<br>")
    # Простая замена **жирного** на <b>
    html_content = html_content.replace("**", "<b>", 1).replace("**", "</b>", 1) if "**" in html_content else html_content
    # Создаём карточку
    st.markdown(f"""
    <div class="presentation-card">
        <div class="slide-header">
            <span class="slide-icon">{icon}</span>
            <h2>{title}</h2>
        </div>
        <div>{html_content}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- АГЕНТЫ (СИСТЕМНЫЕ ПРОМПТЫ) ----------
AGENTS = {
    "Квалификатор": {
        "prompt": """Ты — эксперт по квалификации клиентов. Оценивай лид, используй SPIN-продажи, BANT.
        Ответ оформи в виде продающего резюме: выдели потенциал, риски, предложи следующий шаг. Используй маркированные списки, подзаголовки."""
    },
    "Диагност": {
        "prompt": """Ты — бизнес-аналитик. Проведи SWOT-анализ, выяви корневые проблемы, используй методику 5 почему.
        Представь результат как консалтинговый отчёт с разделами: Ключевые выводы, SWOT, Корневые причины."""
    },
    "Стратег": {
        "prompt": """Ты — стратегический консультант. Разработай 2-3 сценария, оцени риски, предложи дорожную карту.
        Ответ должен содержать заголовки сценариев, плюсы/минусы, рекомендованный путь."""
    },
    "Репортер": {
        "prompt": """Ты — мастер презентаций. Преврати стратегию в структурированный документ для клиента.
        Используй подзаголовки, ключевые тезисы, выделяй главное. Стиль — продающий и убедительный."""
    },
    "Внедренец": {
        "prompt": """Ты — руководитель проектов. Составь подробный план внедрения с этапами, сроками, ответственными.
        Оформи как чек-лист с контрольными точками."""
    },
    "Контролёр": {
        "prompt": """Ты — специалист по KPI. Определи 3-5 SMART-показателей для мониторинга успеха стратегии.
        Предложи формат ежемесячного отчёта."""
    }
}

# ---------- БОКОВАЯ ПАНЕЛЬ ----------
st.sidebar.title("📋 Этапы работы")
этап = st.sidebar.radio(
    "Выберите этап",
    ["1. Квалификация лида", "2. Диагностика", "3. Стратегия",
     "4. Презентация/Отчет", "5. Внедрение", "6. Мониторинг",
     "📊 Полная презентация для клиента"]
)

# ---------- ЭТАП 1 ----------
if этап.startswith("1"):
    st.header("🎯 Квалификация лида")
    with st.form("lead_form"):
        компания = st.text_input("Компания", value=st.session_state.lead_data.get("компания", ""))
        контакт = st.text_input("Контакт", value=st.session_state.lead_data.get("контакт", ""))
        запрос = st.text_area("Описание запроса", value=st.session_state.lead_data.get("потребности", ""))
        if st.form_submit_button("Запустить квалификацию") and client:
            user_msg = f"Компания: {компания}. Контакт: {контакт}. Запрос: {запрос}"
            res = ask_agent(AGENTS["Квалификатор"]["prompt"], user_msg)
            if res:
                st.session_state.lead_data.update(компания=компания, контакт=контакт, потребности=запрос, квалификация=res)
                display_presentation("Квалификация лида", res, "🔍")

    if "квалификация" in st.session_state.lead_data:
        display_presentation("Квалификация лида (сохранено)", st.session_state.lead_data["квалификация"], "🔍")

# ---------- ЭТАП 2 ----------
elif этап.startswith("2"):
    st.header("🔎 Диагностика")
    контекст = st.text_area("Введите данные о ситуации клиента", height=200,
                            value=st.session_state.lead_data.get("диагностика_input", ""))
    файл = st.file_uploader("Загрузить txt-файл", type=["txt"])
    if st.button("Провести диагностику") and client:
        if файл:
            контент = файл.read().decode("utf-8", errors="ignore")
            контекст += "\n\n[Файл]:\n" + контент
        if контекст.strip():
            st.session_state.lead_data["диагностика_input"] = контекст
            res = ask_agent(AGENTS["Диагност"]["prompt"], контекст)
            if res:
                st.session_state.lead_data["диагностика"] = res
                display_presentation("Диагностика бизнеса", res, "📈")
        else:
            st.warning("Введите текст или загрузите файл.")
    if "диагностика" in st.session_state.lead_data:
        display_presentation("Диагностика бизнеса (сохранено)", st.session_state.lead_data["диагностика"], "📈")

# ---------- ЭТАП 3 ----------
elif этап.startswith("3"):
    st.header("🚀 Стратегия")
    if "диагностика" not in st.session_state.lead_data:
        st.warning("Сначала выполните диагностику.")
    elif st.button("Разработать стратегию") and client:
        res = ask_agent(AGENTS["Стратег"]["prompt"], st.session_state.lead_data["диагностика"])
        if res:
            st.session_state.lead_data["стратегия"] = res
            display_presentation("Стратегия развития", res, "🎯")
    if "стратегия" in st.session_state.lead_data:
        display_presentation("Стратегия развития (сохранено)", st.session_state.lead_data["стратегия"], "🎯")

# ---------- ЭТАП 4 ----------
elif этап.startswith("4"):
    st.header("📊 Презентация / Отчёт")
    if "стратегия" not in st.session_state.lead_data:
        st.warning("Сначала создайте стратегию.")
    elif st.button("Сгенерировать отчёт") and client:
        компания = st.session_state.lead_data.get("компания", "Клиент")
        res = ask_agent(AGENTS["Репортер"]["prompt"], f"Компания: {компания}\nСтратегия:\n{st.session_state.lead_data['стратегия']}")
        if res:
            st.session_state.lead_data["отчет"] = res
            display_presentation("Продающая презентация для клиента", res, "📑")
    if "отчет" in st.session_state.lead_data:
        display_presentation("Продающая презентация (сохранено)", st.session_state.lead_data["отчет"], "📑")

# ---------- ЭТАП 5 ----------
elif этап.startswith("5"):
    st.header("⚙️ План внедрения")
    if "стратегия" not in st.session_state.lead_data:
        st.warning("Сначала нужна стратегия.")
    elif st.button("Создать план внедрения") and client:
        res = ask_agent(AGENTS["Внедренец"]["prompt"], st.session_state.lead_data["стратегия"])
        if res:
            st.session_state.lead_data["план_внедрения"] = res
            display_presentation("Детальный план действий", res, "📌")
    if "план_внедрения" in st.session_state.lead_data:
        display_presentation("План внедрения (сохранено)", st.session_state.lead_data["план_внедрения"], "📌")

# ---------- ЭТАП 6 ----------
elif этап.startswith("6"):
    st.header("📈 Мониторинг и KPI")
    if "стратегия" not in st.session_state.lead_data:
        st.warning("Сначала разработайте стратегию.")
    elif st.button("Определить KPI") and client:
        res = ask_agent(AGENTS["Контролёр"]["prompt"], st.session_state.lead_data["стратегия"])
        if res:
            st.session_state.lead_data["мониторинг"] = res
            display_presentation("Система ключевых показателей", res, "📉")
    if "мониторинг" in st.session_state.lead_data:
        display_presentation("KPI (сохранено)", st.session_state.lead_data["мониторинг"], "📉")

# ---------- ПОЛНАЯ ПРЕЗЕНТАЦИЯ ----------
elif этап == "📊 Полная презентация для клиента":
    st.header("🧾 Итоговая презентация для клиента")
    if not any(k in st.session_state.lead_data for k in ["квалификация", "диагностика", "стратегия"]):
        st.info("Пройдите хотя бы первые три этапа, чтобы собрать презентацию.")
    else:
        st.markdown("### Ниже собраны все результаты в едином стиле. Можно скроллить или распечатать.")
        # Кнопка для печати (открывает диалог браузера)
        st.markdown("<script>function printPage() { window.print(); }</script>", unsafe_allow_html=True)
        st.button("🖨️ Распечатать презентацию", on_click=lambda: st.markdown("<script>printPage()</script>", unsafe_allow_html=True))

        if "квалификация" in st.session_state.lead_data:
            display_presentation("1. Квалификация лида", st.session_state.lead_data["квалификация"], "🔍")
        if "диагностика" in st.session_state.lead_data:
            display_presentation("2. Диагностика", st.session_state.lead_data["диагностика"], "📈")
        if "стратегия" in st.session_state.lead_data:
            display_presentation("3. Стратегия", st.session_state.lead_data["стратегия"], "🎯")
        if "отчет" in st.session_state.lead_data:
            display_presentation("4. Финальный отчёт", st.session_state.lead_data["отчет"], "📑")
        if "план_внедрения" in st.session_state.lead_data:
            display_presentation("5. План внедрения", st.session_state.lead_data["план_внедрения"], "📌")
        if "мониторинг" in st.session_state.lead_data:
            display_presentation("6. KPI и мониторинг", st.session_state.lead_data["мониторинг"], "📉")

# ---------- ПОДВАЛ ----------
st.sidebar.markdown("---")
st.sidebar.info("Все данные сессии будут потеряны при обновлении страницы. Для постоянного хранения подключите базу данных.")
