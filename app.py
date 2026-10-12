
import streamlit as st
import pandas as pd
from datetime import date

from gemini_service import (
    extract_deadlines,
    extract_deadlines_from_text,
)
from telegram_service import send_telegram


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DeadlineMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 30px;
        border-radius: 18px;
        background: linear-gradient(120deg, #102a56, #2563eb);
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        font-size: 2.2rem;
        margin-bottom: 10px;
    }

    .hero p {
        color: #e0eaff;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "deadline_result" not in st.session_state:
    st.session_state["deadline_result"] = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("📚 DeadlineMate AI")
    st.caption("Your academic planning assistant")

    st.divider()

    student_name = st.text_input(
        "Your name",
        placeholder="Enter your name",
        key="student_name",
    )

    st.info(
        "Upload a syllabus, timetable, assignment sheet, "
        "or paste academic text to discover deadlines."
    )

    if st.button("🗑️ Clear extracted results", use_container_width=True):
        st.session_state["deadline_result"] = None
        st.rerun()

    st.divider()

    st.caption("Powered by Gemini AI + Telegram")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

display_name = student_name.strip() or "Student"

st.markdown(
    f"""
    <div class="hero">
        <h1>📅 Welcome, {display_name}!</h1>
        <p>
            Plan smarter. Miss nothing. Turn your academic
            documents into organized deadlines and reminders.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("What would you like to analyze?")
st.caption(
    "Upload a document image or enter academic text. "
    "Always verify extracted dates before relying on them."
)


# --------------------------------------------------
# INPUT TABS
# --------------------------------------------------

image_tab, text_tab = st.tabs(
    ["📷 Upload a photo", "✍️ Enter or paste text"]
)


# --------------------------------------------------
# IMAGE INPUT
# --------------------------------------------------

with image_tab:

    uploaded_file = st.file_uploader(
        "Choose an academic document image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of your syllabus or timetable.",
        key="academic_image",
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded document preview",
            use_container_width=True,
        )

        if st.button(
            "✨ Extract deadlines from image",
            type="primary",
            use_container_width=True,
        ):

            try:
                with st.spinner(
                    "Gemini is analyzing your document..."
                ):
                    result = extract_deadlines(
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )

                    st.session_state["deadline_result"] = result

                st.success("Document analyzed successfully!")

            except Exception as error:
                st.error("Unable to analyze this image.")
                st.caption(str(error))


# --------------------------------------------------
# TEXT INPUT
# --------------------------------------------------

with text_tab:

    academic_text = st.text_area(
        "Paste your syllabus details or assignment notice",
        placeholder=(
            "Example:\n"
            "DBMS assignment deadline: 20 October 2026\n"
            "OS lab record submission: 22 October 2026\n"
            "CN internal examination: 25 October 2026"
        ),
        height=200,
        key="academic_text",
    )

    if st.button(
        "✨ Extract deadlines from text",
        type="primary",
        use_container_width=True,
    ):

        if not academic_text.strip():
            st.warning("Please enter some academic text.")

        else:
            try:
                with st.spinner(
                    "Gemini is organizing your deadlines..."
                ):
                    result = extract_deadlines_from_text(
                        academic_text.strip()
                    )

                    st.session_state["deadline_result"] = result

                st.success("Deadlines extracted successfully!")

            except Exception as error:
                st.error("Unable to analyze this text.")
                st.caption(str(error))


# --------------------------------------------------
# DEADLINE DASHBOARD
# --------------------------------------------------


# --------------------------------------------------
# DEADLINE DASHBOARD + TELEGRAM
# --------------------------------------------------

result = st.session_state.get("deadline_result")

if result is not None:
    st.divider()
    st.header("📅 Your Deadline Dashboard")

    deadlines = result.get("deadlines", [])
    notes = result.get("notes", [])

    if deadlines:
        from datetime import date
        import pandas as pd

        today = date.today()
        rows = []

        for item in deadlines:
            due_date = item.get("due_date")
            needs_confirmation = item.get(
                "needs_confirmation", True
            )

            days_remaining = "—"
            status = "Needs confirmation"

            if due_date and not needs_confirmation:
                try:
                    parsed_date = date.fromisoformat(due_date)
                    remaining = (parsed_date - today).days
                    days_remaining = remaining

                    if remaining < 0:
                        status = "Overdue"
                    elif remaining == 0:
                        status = "Due today"
                    else:
                        status = "Upcoming"
                except (ValueError, TypeError):
                    status = "Verify date"

            rows.append({
                "Task": item.get("title", "Untitled"),
                "Subject": item.get("subject", "Unknown"),
                "Due Date": due_date or "Not available",
                "Days Remaining": days_remaining,
                "Priority": item.get("priority", "unknown"),
                "Status": status,
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("📨 Send deadlines to Telegram")

        if st.button(
            "🚀 Send Deadline Summary to Telegram",
            type="primary",
            use_container_width=True,
        ):
            message_lines = [
                "📚 DeadlineMate AI",
                "Your academic deadline summary",
                "",
            ]

            for item in deadlines:
                message_lines.extend([
                    f"📌 {item.get('title', 'Untitled task')}",
                    f"Subject: {item.get('subject', 'Unknown')}",
                    f"Due date: {item.get('due_date') or 'Not available'}",
                    f"Priority: {item.get('priority', 'unknown')}",
                ])

                if item.get("needs_confirmation", True):
                    message_lines.append(
                        "⚠️ Please verify this deadline."
                    )

                message_lines.append("")

            try:
                with st.spinner("Sending Telegram message..."):
                    success, feedback = send_telegram(
                        "\n".join(message_lines)
                    )

                if success:
                    st.success(feedback)
                else:
                    st.error(feedback)

            except Exception as error:
                st.error("Unable to send the Telegram message.")
                st.caption(str(error))

    else:
        st.info(
            "No academic deadlines were found. "
            "Try a syllabus, timetable, or assignment notice."
        )

        st.subheader("📨 Telegram")
        st.caption(
            "The button is available, but a summary can only "
            "be sent after at least one deadline is extracted."
        )
        st.button(
            "🚀 Send Deadline Summary to Telegram",
            disabled=True,
            use_container_width=True,
        )

    if notes:
        st.subheader("📝 Notes and items to verify")
        for note in notes:
            st.write(f"- {note}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <p class="small-note" style="text-align:center;">
        DeadlineMate AI · Study smarter, stay organized.
    </p>
    """,
    unsafe_allow_html=True,
)
