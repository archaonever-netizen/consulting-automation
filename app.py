import streamlit as st
import os
from groq import Groq

# ---------- НАСТРОЙКА ----------
st.set_page_config(page_title="Консалтинг Автоматизация", layout="wide")
st.title("🧠 Система консалтинговой компании с ИИ-агентами")

# Храним API‑ключ в сессии, чтобы не вводить при каждом переключении этапа
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

# Поле для ввода ключа в боковой панели
st.sidebar.text_input(
    "🔑 Введите ваш Groq API Key",
    type="password",
    key="api_key_input",
    on_change=lambda: st.session_state.update(groq_api_key=st.session_state.api_key_input or "")
)

# Создаём клиент только если ключ введён
client = None
if st.session_state.groq_api_key:
    client = Groq(api_key=st.session_state.groq_api_key)

# ---------- ФОНД СЕССИИ ДЛЯ ДАННЫХ КЛИЕНТА ----------
if "lead_data" not in st.session_state:
    st.session_state.lead_data = {
        "компания": "",
        "контакт": "",
        "потребности": "",
        "бюджет": "",
        "сроки": "",
        "диагностика": "",
        "стратегия": "",
        "отчет": "",
        "план_внедрения": ""
    }

# ---------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ЗАПРОСА К LLM ----------
def ask_agent(system_prompt, user_message, model="llama3-70b-8192"):
    if not client:
        st.error("Сначала введите API‑ключ Groq в боковой панели.")
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

# ---------- АГЕНТЫ (СИСТЕМНЫЕ ПРОМПТЫ И НАВЫКИ) ----------
AGENTS = {
    "Квалификатор": {
        "system_prompt": """Ты — эксперт по квалификации клиентов в консалтинге.
Твои навыки: активное слушание, выявление потребностей, SPIN-продажи.
Твои знания: критерии оценки лидов, типология клиентов, BANT (бюджет, полномочия, потребность, сроки).
Твой подход: задавай открытые вопросы, резюмируй ответы, определи потенциал сделки.
В конце дай оценку: горячий / теплый / холодный лид и почему."""
    },
    "Диагност": {
        "system_prompt": """Ты — бизнес-аналитик в консалтинге.
Навыки: глубинный анализ, SWOT, PESTLE, root-cause analysis, интервьюирование.
Знания: отраслевые модели, бенчмаркинг, методика 5 почему.
Подход: изучай ситуацию структурно, выделяй ключевые проблемы и возможности.
На основе предоставленных данных выдай развернутую диагностику с выводами."""
    },
    "Стратег": {
        "system_prompt": """Ты — стратегический консультант.
Навыки: стратегическое мышление, дизайн-мышление, приоритезация, дорожные карты.
Знания: матрица BCG, голубой океан, OKR, модель 7S.
Подход: генерируй 2-3 сценария развития, оценивай риски и выгоды, предлагай оптимальный путь.
На основе диагностики разработай стратегические рекомендации."""
    },
    "Репортер": {
        "system_prompt": """Ты — мастер презентаций и отчетов в консалтинге.
Навыки: сторителлинг, визуальное мышление, структурирование информации.
Знания: принципы MECE, пирамида Минто, формат executive summary.
Подход: преврати стратегию в понятный отчет для клиента с заголовками, ключевыми тезисами и графикой (описанием графиков). Используй Markdown."""
    },
    "Внедренец": {
        "system_prompt": """Ты — руководитель проектов по внедрению изменений.
Навыки: проектное управление, agile/scrum, управление изменениями.
Знания: ADKAR-модель, PMBOK, цикл Деминга.
Подход: создай пошаговый план с действиями, сроками, ответственными и контрольными точками. Учти сопротивление изменениям."""
    },
    "Контролёр": {
        "system_prompt": """Ты — специалист по мониторингу эффективности.
Навыки: KPI-дизайн, сбор обратной связи, аналитика данных.
Знания: SMART-цели, balanced scorecard, метрики консалтинговых проектов.
Подход: определи 3-5 ключевых показателей для отслеживания результатов стратегии и предложи формат регулярного отчета."""
    }
}

# ---------- БОКОВАЯ ПАНЕЛЬ: НАВИГАЦИЯ ПО ЭТАПАМ ----------
st.sidebar.title("Этапы работы с клиентом")
этап = st.sidebar.radio(
    "Перейти к этапу:",
    ["1. Квалификация лида",
     "2. Диагностика",
     "3. Стратегия",
     "4. Презентация/Отчет",
     "5. Внедрение",
     "6. Мониторинг"]
)

# ---------- ЭТАП 1: КВАЛИФИКАЦИЯ ----------
if этап.startswith("1"):
    st.header("🎯 Квалификация лида")
    st.write("Агент-квалификатор поможет вам задать правильные вопросы и оценить потенциал.")

    with st.form("lead_form"):
        компания = st.text_input("Название компании клиента", value=st.session_state.lead_data["компания"])
        контакт = st.text_input("Контактное лицо", value=st.session_state.lead_data["контакт"])
        запрос = st.text_area("Опишите первичный запрос или результаты разговора", value=st.session_state.lead_data["потребности"])
        submitted = st.form_submit_button("Передать агенту на квалификацию")

    if submitted and client:
        user_msg = f"Компания: {компания}. Контакт: {контакт}. Запрос: {запрос}"
        результат = ask_agent(AGENTS["Квалификатор"]["system_prompt"], user_msg)
        if результат:
            st.session_state.lead_data["компания"] = компания
            st.session_state.lead_data["контакт"] = контакт
            st.session_state.lead_data["потребности"] = запрос
            st.session_state.lead_data["квалификация"] = результат
            st.success("Готово! Результат ниже:")
            st.markdown(результат)

    if st.session_state.lead_data.get("квалификация"):
        st.subheader("Результат квалификации:")
        st.markdown(st.session_state.lead_data["квалификация"])

# ---------- ЭТАП 2: ДИАГНОСТИКА ----------
elif этап.startswith("2"):
    st.header("🔍 Диагностика")
    st.write("Предоставьте информацию о ситуации клиента для агента-аналитика.")

    контекст = st.text_area(
        "Опишите текущую ситуацию, симптомы, цифры, рыночные условия",
        value=st.session_state.lead_data.get("диагностика_input", ""),
        height=200
    )
    загруженный_файл = st.file_uploader("Или загрузите файл (txt, csv, pdf пока не поддерживается)", type=["txt"])

    if st.button("Запустить диагностику") and client:
        if загруженный_файл:
            контент = загруженный_файл.read().decode("utf-8", errors="ignore")
            контекст += "\n\n[Содержимое файла]:\n" + контент
        if контекст.strip():
            st.session_state.lead_data["диагностика_input"] = контекст
            результат = ask_agent(AGENTS["Диагност"]["system_prompt"], контекст)
            if результат:
                st.session_state.lead_data["диагностика"] = результат
                st.success("Диагностика завершена!")
                st.markdown(результат)
        else:
            st.warning("Введите описание или загрузите файл.")

    if st.session_state.lead_data.get("диагностика"):
        st.subheader("Результаты диагностики:")
        st.markdown(st.session_state.lead_data["диагностика"])

# ---------- ЭТАП 3: СТРАТЕГИЯ ----------
elif этап.startswith("3"):
    st.header("🚀 Разработка стратегии")

    if not st.session_state.lead_data.get("диагностика"):
        st.warning("Сначала проведите диагностику на этапе 2.")
    elif st.button("Сгенерировать стратегию") and client:
        результат = ask_agent(AGENTS["Стратег"]["system_prompt"], st.session_state.lead_data["диагностика"])
        if результат:
            st.session_state.lead_data["стратегия"] = результат
            st.success("Стратегия готова!")
            st.markdown(результат)

    if st.session_state.lead_data.get("стратегия"):
        st.subheader("Итоговая стратегия:")
        st.markdown(st.session_state.lead_data["стратегия"])

# ---------- ЭТАП 4: ОТЧЕТ/ПРЕЗЕНТАЦИЯ ----------
elif этап.startswith("4"):
    st.header("📊 Презентация и отчет")
    if not st.session_state.lead_data.get("стратегия"):
        st.warning("Сначала разработайте стратегию (этап 3).")
    elif st.button("Создать отчёт") and client:
        результат = ask_agent(AGENTS["Репортер"]["system_prompt"],
                              f"Компания: {st.session_state.lead_data.get('компания', '')} Стратегия: {st.session_state.lead_data['стратегия']}")
        if результат:
            st.session_state.lead_data["отчет"] = результат
            st.success("Отчёт готов!")
            st.markdown(результат)
    if st.session_state.lead_data.get("отчет"):
        st.subheader("Финальный отчёт:")
        st.markdown(st.session_state.lead_data["отчет"])

# ---------- ЭТАП 5: ВНЕДРЕНИЕ ----------
elif этап.startswith("5"):
    st.header("⚙️ План внедрения")
    if not st.session_state.lead_data.get("стратегия"):
        st.warning("Сначала нужна стратегия (этап 3).")
    elif st.button("Разработать план внедрения") and client:
        результат = ask_agent(AGENTS["Внедренец"]["system_prompt"], st.session_state.lead_data["стратегия"])
        if результат:
            st.session_state.lead_data["план_внедрения"] = результат
            st.success("План готов!")
            st.markdown(результат)
    if st.session_state.lead_data.get("план_внедрения"):
        st.subheader("План внедрения:")
        st.markdown(st.session_state.lead_data["план_внедрения"])

# ---------- ЭТАП 6: МОНИТОРИНГ ----------
elif этап.startswith("6"):
    st.header("📈 Мониторинг и KPI")
    if not st.session_state.lead_data.get("стратегия"):
        st.warning("Сначала разработайте стратегию (этап 3).")
    elif st.button("Сформировать систему KPI") and client:
        результат = ask_agent(AGENTS["Контролёр"]["system_prompt"], st.session_state.lead_data["стратегия"])
        if результат:
            st.session_state.lead_data["мониторинг"] = результат
            st.success("Метрики определены!")
            st.markdown(результат)
    if st.session_state.lead_data.get("мониторинг"):
        st.subheader("Система мониторинга:")
        st.markdown(st.session_state.lead_data["мониторинг"])

# ---------- ПОДВАЛ ----------
st.sidebar.markdown("---")
st.sidebar.info(
    "Все данные хранятся только в рамках вашей сессии. "
    "Для реального использования добавьте базу данных.\n\n"
    "Разработано на Streamlit + Groq (Llama 3)."
)
