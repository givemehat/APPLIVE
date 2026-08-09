import streamlit as st
import json
import os
import sys

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RiskIQ — AI Investment Profiler",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0d0d1a;
    color: #e0e0e0;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    font-size: 15px;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1, #9333ea);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.4);
}

/* Cards */
.card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

.badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 20px;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 0.5px;
}

.badge-conservative { background: #1a3d1a; color: #4CAF50; border: 1px solid #4CAF50; }
.badge-moderate     { background: #3d2e1a; color: #FF9800; border: 1px solid #FF9800; }
.badge-aggressive   { background: #3d1a1a; color: #F44336; border: 1px solid #F44336; }

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}

.hero-sub {
    font-size: 1.1rem;
    color: #888;
    margin-top: 0.5rem;
}

.stat-card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

.stat-val {
    font-size: 2rem;
    font-weight: 700;
    color: #818cf8;
}

.stat-label {
    font-size: 0.8rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.question-label {
    font-size: 1rem;
    font-weight: 500;
    color: #ccc;
    margin-bottom: 0.3rem;
}

.advice-box {
    background: #13131f;
    border-left: 4px solid #818cf8;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    font-size: 0.95rem;
    color: #bbb;
    line-height: 1.7;
}

.alloc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e1e3a;
}

.step-badge {
    background: #1e1e3a;
    color: #818cf8;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    margin-right: 8px;
}

/* Sliders */
.stSlider > div > div { background: #2a2a4a !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: #1a1a2e !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px;
    color: white;
}

/* Radio */
.stRadio > div { gap: 10px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #888;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
}

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: #2a2a4a; }
</style>
""",
    unsafe_allow_html=True,
)


# ─── ENSURE MODEL EXISTS ──────────────────────────────────────────────────────
@st.cache_resource
def load_model_files():
    if not os.path.exists("risk_model.pkl"):
        with st.spinner("Training AI model for the first time... (~10 seconds)"):
            # Generate data
            exec(open("dataset.py").read())
            import model as m

            m.train_model()
    return True


load_model_files()

from model import predict_risk
from utils import (
    make_gauge_chart,
    make_pie_chart,
    make_comparison_bar,
    make_probability_bar,
    save_profile,
    load_all_profiles,
    get_ai_advice,
    generate_pdf_report,
    PORTFOLIO_ALLOCATIONS,
    CATEGORY_COLORS,
)

# ─── LOAD QUESTIONS ──────────────────────────────────────────────────────────
with open("risk_questions.json") as f:
    QUESTIONS = json.load(f)

# ─── SESSION STATE ───────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "result" not in st.session_state:
    st.session_state.result = None


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    # Hero
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(
            '<div class="hero-title">Know Your<br>Investment DNA</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="hero-sub">AI-powered risk profiling in under 2 minutes.<br>Get personalized portfolio advice backed by ML.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀  Start Risk Assessment", key="start"):
            st.session_state.page = "quiz"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Stats row
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                '<div class="stat-card"><div class="stat-val">1,200+</div><div class="stat-label">Training Samples</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                '<div class="stat-card"><div class="stat-val">3</div><div class="stat-label">Risk Profiles</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                '<div class="stat-card"><div class="stat-val">ML+AI</div><div class="stat-label">Powered</div></div>',
                unsafe_allow_html=True,
            )

    with col2:
        # Feature cards
        features = [
            (
                "🧠",
                "Machine Learning Model",
                "Logistic Regression trained on 1,200+ investor profiles",
            ),
            (
                "📊",
                "Visual Analytics",
                "Gauge, pie, and bar charts for complete clarity",
            ),
            (
                "🤖",
                "AI Personalized Advice",
                "GPT-powered recommendations tailored to you",
            ),
            ("📄", "PDF Report", "Download your full investment report instantly"),
        ]
        for icon, title, desc in features:
            st.markdown(
                f"""
            <div class="card">
                <div style="font-size:1.5rem">{icon}</div>
                <div style="font-weight:600;color:#ccc;margin:4px 0">{title}</div>
                <div style="font-size:0.85rem;color:#666">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # How it works
    st.markdown(
        '<div style="font-size:1.3rem;font-weight:700;color:#ccc;margin-bottom:1rem">How It Works</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    steps = [
        ("1", "Answer 7 Questions", "About your age, income, goals & behavior"),
        ("2", "ML Analyzes You", "Model scores and classifies your risk type"),
        ("3", "Get Your Profile", "Visualized with charts and confidence scores"),
        ("4", "Receive Advice", "AI gives actionable investment guidance"),
    ]
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
            <div class="stat-card" style="text-align:left;padding:1.2rem">
                <span class="step-badge">{num}</span>
                <div style="font-weight:600;color:#ccc;margin:8px 0 4px">{title}</div>
                <div style="font-size:0.82rem;color:#555">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("View Admin Dashboard →", key="admin_link"):
            st.session_state.page = "admin"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: QUIZ
# ═══════════════════════════════════════════════════════════════════════════════
def page_quiz():
    st.markdown(
        '<div style="font-size:1.6rem;font-weight:700;color:#ccc;margin-bottom:0.3rem">📋 Investment Risk Assessment</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:#555;margin-bottom:1.5rem">Answer honestly — your results are only as good as your inputs.</div>',
        unsafe_allow_html=True,
    )

    with st.form("quiz_form"):
        # Q1 — Age
        q = QUESTIONS[0]
        st.markdown(
            f'<div class="question-label">1. {q["label"]}</div>', unsafe_allow_html=True
        )
        age = st.slider(
            "",
            min_value=18,
            max_value=70,
            value=30,
            key="age",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Q2 — Monthly Income
        q = QUESTIONS[1]
        st.markdown(
            f'<div class="question-label">2. {q["label"]}</div>', unsafe_allow_html=True
        )
        income = st.select_slider(
            "",
            options=[5000, 10000, 20000, 35000, 50000, 75000, 100000, 150000, 200000],
            format_func=lambda x: f"₹{x:,}",
            value=35000,
            key="income",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Q3 — Experience
        q = QUESTIONS[2]
        st.markdown(
            f'<div class="question-label">3. {q["label"]}</div>', unsafe_allow_html=True
        )
        experience = st.slider(
            "",
            min_value=0,
            max_value=30,
            value=3,
            key="exp",
            label_visibility="collapsed",
        )
        st.caption(
            f'{"🔰 Beginner" if experience < 2 else "📈 Intermediate" if experience < 7 else "🏆 Expert"} — {experience} year(s)'
        )

        st.markdown("---")

        # Q4 — Risk Tolerance
        q = QUESTIONS[3]
        st.markdown(
            f'<div class="question-label">4. {q["label"]}</div>', unsafe_allow_html=True
        )
        risk_tol = st.radio(
            "",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 — Very Low (Sleep is priceless)",
                2: "2 — Low (Small dips bother me)",
                3: "3 — Medium (I can handle some ups & downs)",
                4: "4 — High (I embrace volatility)",
                5: "5 — Very High (Bring on the rollercoaster!)",
            }[x],
            key="risk_tol",
            label_visibility="collapsed",
            horizontal=False,
        )

        st.markdown("---")

        # Q5 — Investment Horizon
        q = QUESTIONS[4]
        st.markdown(
            f'<div class="question-label">5. {q["label"]}</div>', unsafe_allow_html=True
        )
        horizon_label = st.selectbox(
            "",
            options=[
                "< 6 months",
                "6–12 months",
                "1–3 years",
                "3–7 years",
                "7–15 years",
                "15+ years",
            ],
            key="horizon",
            label_visibility="collapsed",
        )
        horizon_map = {
            "< 6 months": 3,
            "6–12 months": 9,
            "1–3 years": 24,
            "3–7 years": 60,
            "7–15 years": 120,
            "15+ years": 240,
        }
        horizon = horizon_map[horizon_label]

        st.markdown("---")

        # Q6 — Financial Goal
        q = QUESTIONS[5]
        st.markdown(
            f'<div class="question-label">6. {q["label"]}</div>', unsafe_allow_html=True
        )
        goal = st.radio(
            "",
            options=["wealth", "retirement", "education", "emergency"],
            format_func=lambda x: {
                "wealth": "💰 Wealth Creation",
                "retirement": "🏖️ Retirement Planning",
                "education": "🎓 Education Fund",
                "emergency": "🛡️ Emergency Reserve",
            }[x],
            key="goal",
            label_visibility="collapsed",
            horizontal=True,
        )

        st.markdown("---")

        # Q7 — Loss Reaction
        q = QUESTIONS[6]
        st.markdown(
            f'<div class="question-label">7. {q["label"]}</div>', unsafe_allow_html=True
        )
        behavior = st.radio(
            "",
            options=["panic-sell", "hold", "buy-more"],
            format_func=lambda x: {
                "panic-sell": "😰 Sell everything immediately",
                "hold": "😐 Hold and wait it out",
                "buy-more": "😎 Buy more at lower prices",
            }[x],
            key="behavior",
            label_visibility="collapsed",
            horizontal=False,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "🔍  Analyze My Risk Profile", use_container_width=True
        )

    if submitted:
        user_data = {
            "Age": age,
            "Monthly_Income": income,
            "Investment_Experience": experience,
            "Risk_Tolerance": risk_tol,
            "Investment_Horizon": horizon,
            "Financial_Goal": goal,
            "Loss_Reaction": behavior,
        }

        with st.spinner("Running ML model and generating AI advice..."):
            category, score, prob_dict = predict_risk(user_data)
            advice = get_ai_advice(user_data, category, prob_dict)
            save_profile(user_data, category, score)

        st.session_state.result = {
            "user_data": user_data,
            "category": category,
            "score": score,
            "prob_dict": prob_dict,
            "advice": advice,
            "horizon_label": horizon_label,
        }
        st.session_state.page = "result"
        st.rerun()

    st.markdown("<br>")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: RESULT
# ═══════════════════════════════════════════════════════════════════════════════
def page_result():
    r = st.session_state.result
    if not r:
        st.session_state.page = "home"
        st.rerun()

    user_data = r["user_data"]
    category = r["category"]
    score = r["score"]
    prob_dict = r["prob_dict"]
    advice = r["advice"]

    cat_lower = category.lower()
    badge_class = f"badge-{cat_lower}"

    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f'<div style="font-size:1.8rem;font-weight:700;color:#ccc">Your Investment Risk Profile</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<br><span class="badge {badge_class}">🎯 {category} Investor</span>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("🔄  Retake Assessment"):
            st.session_state.page = "quiz"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Gauge + Pie ──
    col_g, col_p = st.columns(2)
    with col_g:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_gauge = make_gauge_chart(score, category)
        st.plotly_chart(
            fig_gauge, use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_p:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_pie = make_pie_chart(category)
        st.plotly_chart(
            fig_pie, use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Probability Bar + Comparison ──
    col_pb, col_cmp = st.columns(2)
    with col_pb:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_prob = make_probability_bar(prob_dict)
        st.plotly_chart(
            fig_prob, use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cmp:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig_cmp = make_comparison_bar(user_data, category)
        if fig_cmp:
            st.plotly_chart(
                fig_cmp, use_container_width=True, config={"displayModeBar": False}
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 3: Allocation table + Profile summary ──
    col_t, col_s = st.columns([1, 1])
    with col_t:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-weight:600;color:#ccc;margin-bottom:0.8rem">📌 Recommended Allocation</div>',
            unsafe_allow_html=True,
        )
        alloc = PORTFOLIO_ALLOCATIONS[category]
        color = CATEGORY_COLORS[category]
        for asset, pct in alloc.items():
            bar_width = pct
            st.markdown(
                f"""
            <div class="alloc-row">
                <span style="color:#aaa;font-size:0.9rem">{asset}</span>
                <div style="flex:1;margin:0 1rem;background:#1e1e3a;border-radius:4px;height:8px">
                    <div style="width:{bar_width}%;background:{color};border-radius:4px;height:100%"></div>
                </div>
                <span style="font-weight:700;color:{color}">{pct}%</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-weight:600;color:#ccc;margin-bottom:0.8rem">👤 Your Profile Summary</div>',
            unsafe_allow_html=True,
        )
        summary_items = [
            ("Age", f"{user_data['Age']} years"),
            ("Monthly Income", f"₹{user_data['Monthly_Income']:,}"),
            ("Experience", f"{user_data['Investment_Experience']} years"),
            ("Risk Tolerance", f"{user_data['Risk_Tolerance']} / 5"),
            ("Horizon", r["horizon_label"]),
            ("Goal", user_data["Financial_Goal"].title()),
            ("Loss Behavior", user_data["Loss_Reaction"].replace("-", " ").title()),
        ]
        for label, val in summary_items:
            st.markdown(
                f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e1e3a">
                <span style="color:#666;font-size:0.88rem">{label}</span>
                <span style="color:#ccc;font-size:0.88rem;font-weight:500">{val}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Advice ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-weight:600;color:#ccc;margin-bottom:0.8rem">🤖 AI Financial Advisor Says</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="advice-box">{advice.replace(chr(10), "<br><br>")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── PDF Download ──
    st.markdown("<br>", unsafe_allow_html=True)
    col_pdf, col_home = st.columns(2)
    with col_pdf:
        pdf_bytes = generate_pdf_report(user_data, category, score, prob_dict, advice)
        if pdf_bytes:
            st.download_button(
                label="📄  Download PDF Report",
                data=pdf_bytes,
                file_name=f"RiskIQ_Report_{category}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info("Install `fpdf2` to enable PDF download.")

    with col_home:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
def page_admin():
    st.markdown(
        '<div style="font-size:1.6rem;font-weight:700;color:#ccc;margin-bottom:1rem">🛠️ Admin Dashboard</div>',
        unsafe_allow_html=True,
    )

    df = load_all_profiles()

    if df.empty:
        st.info("No profiles yet. Complete the assessment to see data here.")
    else:
        # KPIs
        total = len(df)
        avg_score = df["risk_score"].mean()
        top_cat = df["risk_category"].value_counts().idxmax()

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label in [
            (c1, total, "Total Profiles"),
            (c2, f"{avg_score:.1f}", "Avg Risk Score"),
            (c3, top_cat, "Most Common Type"),
            (c4, df["risk_category"].nunique(), "Categories Found"),
        ]:
            with col:
                st.markdown(
                    f'<div class="stat-card"><div class="stat-val">{val}</div><div class="stat-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Category distribution chart
        import plotly.express as px

        cat_counts = df["risk_category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        color_map = {
            "Conservative": "#4CAF50",
            "Moderate": "#FF9800",
            "Aggressive": "#F44336",
        }

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_dist = px.bar(
                cat_counts,
                x="Category",
                y="Count",
                color="Category",
                color_discrete_map=color_map,
                title="Profile Distribution",
            )
            fig_dist.update_layout(
                paper_bgcolor="#12121f",
                plot_bgcolor="#12121f",
                font=dict(color="white"),
                showlegend=False,
                height=280,
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(
                fig_dist, use_container_width=True, config={"displayModeBar": False}
            )

        with col_chart2:
            fig_scatter = px.scatter(
                df,
                x="age",
                y="risk_score",
                color="risk_category",
                color_discrete_map=color_map,
                title="Age vs Risk Score",
                labels={"age": "Age", "risk_score": "Risk Score"},
            )
            fig_scatter.update_layout(
                paper_bgcolor="#12121f",
                plot_bgcolor="#12121f",
                font=dict(color="white"),
                height=280,
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(
                fig_scatter, use_container_width=True, config={"displayModeBar": False}
            )

        # Score over time
        if len(df) > 1:
            fig_line = px.line(
                df.sort_values("id"),
                x="id",
                y="risk_score",
                color="risk_category",
                color_discrete_map=color_map,
                title="Risk Score Over Time (by Profile ID)",
                markers=True,
            )
            fig_line.update_layout(
                paper_bgcolor="#12121f",
                plot_bgcolor="#12121f",
                font=dict(color="white"),
                height=250,
                margin=dict(l=40, r=20, t=50, b=40),
            )
            st.plotly_chart(
                fig_line, use_container_width=True, config={"displayModeBar": False}
            )

        # Table
        st.markdown(
            '<div style="font-weight:600;color:#ccc;margin:1rem 0 0.5rem">All Profiles</div>',
            unsafe_allow_html=True,
        )
        display_df = df.copy()
        display_df["risk_score"] = display_df["risk_score"].apply(lambda x: f"{x:.1f}")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("<br>")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ─── ROUTER ──────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    page_home()
elif page == "quiz":
    page_quiz()
elif page == "result":
    page_result()
elif page == "admin":
    page_admin()
