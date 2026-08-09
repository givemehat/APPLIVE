import sqlite3
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── PORTFOLIO ───────────────────────────────────────────────────────────────

PORTFOLIO_ALLOCATIONS = {
    "Conservative": {
        "Bonds": 70,
        "ETF": 20,
        "Gold": 10,
    },
    "Moderate": {
        "Stocks": 50,
        "ETF": 30,
        "Bonds": 20,
    },
    "Aggressive": {
        "Stocks": 80,
        "Crypto": 15,
        "ETF": 5,
    },
}

CATEGORY_COLORS = {
    "Conservative": "#4CAF50",
    "Moderate": "#FF9800",
    "Aggressive": "#F44336",
}

PORTFOLIO_COLORS = {
    "Conservative": ["#1a6b3c", "#2e9c5a", "#52c080"],
    "Moderate": ["#1a3f6b", "#2e639c", "#5290c0"],
    "Aggressive": ["#6b1a1a", "#9c2e2e", "#c05252"],
}


# ─── CHARTS ──────────────────────────────────────────────────────────────────


def make_gauge_chart(score: float, category: str):
    color = CATEGORY_COLORS[category]
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=score,
            number={"font": {"size": 48, "color": "white"}},
            delta={
                "reference": 50,
                "increasing": {"color": "#F44336"},
                "decreasing": {"color": "#4CAF50"},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#aaa",
                    "tickfont": {"color": "#aaa"},
                },
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "#1e1e2e",
                "bordercolor": "#333",
                "steps": [
                    {"range": [0, 33], "color": "#1a2e1a"},
                    {"range": [33, 66], "color": "#2e2a1a"},
                    {"range": [66, 100], "color": "#2e1a1a"},
                ],
                "threshold": {
                    "line": {"color": color, "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
            title={
                "text": f"<b>Risk Score</b><br><span style='color:{color};font-size:18px'>{category}</span>",
                "font": {"color": "white", "size": 16},
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="#12121f",
        plot_bgcolor="#12121f",
        height=300,
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig


def make_pie_chart(category: str):
    alloc = PORTFOLIO_ALLOCATIONS[category]
    labels = list(alloc.keys())
    values = list(alloc.values())
    colors = PORTFOLIO_COLORS[category]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#12121f", width=3)),
            textinfo="label+percent",
            textfont=dict(color="white", size=13),
            hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
        )
    )
    fig.update_layout(
        paper_bgcolor="#12121f",
        plot_bgcolor="#12121f",
        showlegend=True,
        legend=dict(font=dict(color="white"), bgcolor="#1e1e2e", bordercolor="#333"),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[
            dict(
                text=f"<b>{category}</b>",
                x=0.5,
                y=0.5,
                font=dict(size=14, color=CATEGORY_COLORS[category]),
                showarrow=False,
            )
        ],
    )
    return fig


def make_comparison_bar(user_data: dict, category: str):
    avg_path = "avg_profiles.json"
    if not os.path.exists(avg_path):
        return None

    with open(avg_path) as f:
        avg = json.load(f)

    metrics = ["Age", "Investment_Experience", "Risk_Tolerance", "Investment_Horizon"]
    labels_map = {
        "Age": "Age",
        "Investment_Experience": "Exp (yrs)",
        "Risk_Tolerance": "Risk Tol",
        "Investment_Horizon": "Horizon (mo)",
    }

    # Normalize to 0–1 for comparison
    ranges = {
        "Age": (22, 65),
        "Investment_Experience": (0, 30),
        "Risk_Tolerance": (1, 5),
        "Investment_Horizon": (6, 360),
    }

    user_norm = []
    avg_norm_cons = []
    avg_norm_mod = []
    avg_norm_agg = []

    for m in metrics:
        lo, hi = ranges[m]
        user_val = user_data.get(m, (lo + hi) / 2)
        user_norm.append((user_val - lo) / (hi - lo) * 100)
        avg_norm_cons.append(
            (avg.get("Conservative", {}).get(m, lo) - lo) / (hi - lo) * 100
        )
        avg_norm_mod.append((avg.get("Moderate", {}).get(m, lo) - lo) / (hi - lo) * 100)
        avg_norm_agg.append(
            (avg.get("Aggressive", {}).get(m, lo) - lo) / (hi - lo) * 100
        )

    x_labels = [labels_map[m] for m in metrics]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="You",
            x=x_labels,
            y=user_norm,
            marker_color=CATEGORY_COLORS[category],
            opacity=0.9,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Avg Conservative",
            x=x_labels,
            y=avg_norm_cons,
            marker_color="#4CAF50",
            opacity=0.4,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Avg Moderate",
            x=x_labels,
            y=avg_norm_mod,
            marker_color="#FF9800",
            opacity=0.4,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Avg Aggressive",
            x=x_labels,
            y=avg_norm_agg,
            marker_color="#F44336",
            opacity=0.4,
        )
    )

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#12121f",
        plot_bgcolor="#12121f",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#2a2a3e"),
        yaxis=dict(gridcolor="#2a2a3e", title="Normalized Score (%)"),
        legend=dict(bgcolor="#1e1e2e", bordercolor="#333", font=dict(color="white")),
        height=340,
        margin=dict(l=40, r=20, t=40, b=40),
        title=dict(
            text="Your Profile vs. Category Averages", font=dict(color="white", size=14)
        ),
    )
    return fig


def make_probability_bar(prob_dict: dict):
    cats = ["Conservative", "Moderate", "Aggressive"]
    vals = [prob_dict.get(c, 0) * 100 for c in cats]
    colors = [CATEGORY_COLORS[c] for c in cats]

    fig = go.Figure(
        go.Bar(
            x=cats,
            y=vals,
            marker_color=colors,
            text=[f"{v:.1f}%" for v in vals],
            textposition="outside",
            textfont=dict(color="white"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#12121f",
        plot_bgcolor="#12121f",
        font=dict(color="white"),
        yaxis=dict(range=[0, 110], gridcolor="#2a2a3e", title="Probability (%)"),
        xaxis=dict(gridcolor="#2a2a3e"),
        height=280,
        margin=dict(l=40, r=20, t=40, b=40),
        title=dict(
            text="Model Confidence per Category", font=dict(color="white", size=14)
        ),
    )
    return fig


# ─── DATABASE ────────────────────────────────────────────────────────────────


def init_db():
    conn = sqlite3.connect("profiles.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            age INTEGER,
            monthly_income INTEGER,
            investment_experience INTEGER,
            risk_tolerance INTEGER,
            investment_horizon INTEGER,
            financial_goal TEXT,
            loss_reaction TEXT,
            risk_category TEXT,
            risk_score REAL
        )
    """)
    conn.commit()
    conn.close()


def save_profile(user_data: dict, category: str, score: float):
    init_db()
    conn = sqlite3.connect("profiles.db")
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO profiles (timestamp, age, monthly_income, investment_experience,
                              risk_tolerance, investment_horizon, financial_goal,
                              loss_reaction, risk_category, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_data["Age"],
            user_data["Monthly_Income"],
            user_data["Investment_Experience"],
            user_data["Risk_Tolerance"],
            user_data["Investment_Horizon"],
            user_data["Financial_Goal"],
            user_data["Loss_Reaction"],
            category,
            score,
        ),
    )
    conn.commit()
    conn.close()


def load_all_profiles():
    init_db()
    conn = sqlite3.connect("profiles.db")
    df = pd.read_sql_query("SELECT * FROM profiles ORDER BY id DESC", conn)
    conn.close()
    return df


# ─── AI ADVICE ───────────────────────────────────────────────────────────────


def get_ai_advice(user_data: dict, category: str, prob_dict: dict) -> str:
    try:
        from openai import OpenAI
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No API key")

        client = OpenAI(api_key=api_key)
        alloc = PORTFOLIO_ALLOCATIONS[category]
        alloc_str = ", ".join([f"{v}% {k}" for k, v in alloc.items()])

        prompt = f"""You are a senior financial advisor. Based on this investor profile, give personalized investment advice in exactly 3 short paragraphs (150 words total):

Profile:
- Age: {user_data['Age']}
- Monthly Income: ₹{user_data['Monthly_Income']:,}
- Investment Experience: {user_data['Investment_Experience']} years
- Risk Tolerance: {user_data['Risk_Tolerance']}/5
- Investment Horizon: {user_data['Investment_Horizon']} months
- Financial Goal: {user_data['Financial_Goal']}
- Loss Reaction: {user_data['Loss_Reaction']}
- Risk Category: {category}
- Suggested Portfolio: {alloc_str}

Paragraph 1: Why this risk profile fits them.
Paragraph 2: How to implement the portfolio allocation.
Paragraph 3: One specific action to take this week.
Be direct, warm, and practical. No jargon."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a certified financial advisor who gives clear, actionable advice.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        # Fallback advice (no API needed)
        fallback = {
            "Conservative": (
                "Your profile shows a preference for stability and capital preservation. "
                "With a lower risk tolerance and cautious market behavior, protecting your "
                "wealth takes priority over high returns.\n\n"
                "Your suggested 70% Bonds, 20% ETF, and 10% Gold portfolio balances safety "
                "with modest growth. Consider government bonds like PPF or NSC for the bond "
                "portion, and a broad market index ETF for equity exposure.\n\n"
                "This week: Open a PPF account if you don't have one, and set up a monthly "
                "SIP of even ₹500 into a liquid debt fund to start building discipline."
            ),
            "Moderate": (
                "You balance growth ambitions with measured caution — a hallmark of a "
                "seasoned, rational investor. Your profile suggests you can handle market "
                "fluctuations without panic, making you ideal for a diversified approach.\n\n"
                "The 50% Stocks, 30% ETF, 20% Bonds mix gives you solid upside while "
                "cushioning downturns. Focus on large-cap stocks and Nifty 50 ETFs for "
                "core positions, with bond funds for stability.\n\n"
                "This week: Review your existing SIPs or start one in a Nifty 50 index fund "
                "— even ₹1,000/month compounds significantly over your investment horizon."
            ),
            "Aggressive": (
                "You have the profile of a growth-seeking investor — young enough to ride "
                "volatility, experienced enough to understand it, and goal-oriented enough "
                "to stay the course during downturns. This is a powerful combination.\n\n"
                "Your 80% Stocks, 15% Crypto, 5% ETF portfolio is high-octane. Prioritize "
                "small/mid-cap stocks and sector ETFs. Keep crypto to established assets "
                "like BTC/ETH and never invest more than you can afford to lose entirely.\n\n"
                "This week: Set a hard stop-loss rule for your crypto positions (e.g., sell "
                "if down 30%) and rebalance your portfolio every quarter without emotion."
            ),
        }
        return fallback[category]


# ─── PDF REPORT ──────────────────────────────────────────────────────────────


def generate_pdf_report(
    user_data: dict, category: str, score: float, prob_dict: dict, advice: str
) -> bytes:
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_fill_color(18, 18, 31)
                self.rect(0, 0, 210, 297, "F")
                self.set_font("Helvetica", "B", 22)
                self.set_text_color(255, 255, 255)
                self.cell(
                    0, 15, "AI Investment Risk Profile Report", ln=True, align="C"
                )
                self.set_font("Helvetica", "", 10)
                self.set_text_color(160, 160, 160)
                self.cell(
                    0,
                    8,
                    f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
                    ln=True,
                    align="C",
                )
                self.ln(5)

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Category badge
        cat_color = {
            "Conservative": (76, 175, 80),
            "Moderate": (255, 152, 0),
            "Aggressive": (244, 67, 54),
        }
        r, g, b = cat_color[category]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(
            0,
            12,
            f"  Risk Category: {category}  |  Risk Score: {score}/100",
            ln=True,
            align="C",
            fill=True,
        )
        pdf.ln(6)

        # User Profile Section
        def section_title(title):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(200, 200, 255)
            pdf.set_fill_color(30, 30, 50)
            pdf.cell(0, 9, f"  {title}", ln=True, fill=True)
            pdf.ln(2)

        def row(label, value):
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(180, 180, 180)
            pdf.cell(80, 8, f"  {label}:", border=0)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 8, str(value), ln=True)

        section_title("Your Profile")
        row("Age", f"{user_data['Age']} years")
        row("Monthly Income", f"Rs. {user_data['Monthly_Income']:,}")
        row("Investment Experience", f"{user_data['Investment_Experience']} years")
        row("Risk Tolerance", f"{user_data['Risk_Tolerance']} / 5")
        row("Investment Horizon", f"{user_data['Investment_Horizon']} months")
        row("Financial Goal", user_data["Financial_Goal"].title())
        row("Loss Reaction", user_data["Loss_Reaction"].replace("-", " ").title())

        pdf.ln(5)
        section_title("Model Confidence")
        for cat, prob in prob_dict.items():
            row(cat, f"{prob * 100:.1f}%")

        pdf.ln(5)
        section_title("Recommended Portfolio Allocation")
        alloc = PORTFOLIO_ALLOCATIONS[category]
        for asset, pct in alloc.items():
            row(asset, f"{pct}%")

        pdf.ln(5)
        section_title("AI Financial Advice")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(210, 210, 210)
        pdf.multi_cell(0, 7, advice)

        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(
            0,
            6,
            "Disclaimer: This report is AI-generated for educational purposes only. Consult a SEBI-registered advisor before investing.",
            ln=True,
            align="C",
        )

        return pdf.output(dest="S").encode("latin-1")

    except Exception as e:
        return b""
