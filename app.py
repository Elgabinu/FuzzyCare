import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from fuzzy_system import assess_health


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FuzzyCare",
    page_icon="🏥",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

if "history" not in st.session_state:
    st.session_state.history = []


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #f7f9fc;
}

/* Main content text */
.stApp p,
.stApp li,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #263746 !important;
}

/* Main headings */
h1, h2, h3 {
    color: #173b4a !important;
}

/* Header captions */
.stCaption {
    color: #64748b !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5eaf0;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #173b4a !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input {
    color: #263746 !important;
    background-color: #ffffff !important;
    border: 1px solid #d5dde5;
}

/* Select and radio labels */
.stRadio label {
    color: #263746 !important;
}

/* Buttons */
.stButton > button {
    background-color: #009688;
    color: #ffffff !important;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}

.stButton > button p {
    color: #ffffff !important;
}

.stButton > button:hover {
    background-color: #00796b;
    color: #ffffff !important;
}

/* Download button */
.stDownloadButton button {
    background-color: #009688;
    color: white !important;
}

/* Information messages */
div[data-testid="stAlert"] p {
    color: #263746 !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    background-color: white;
}

/* Dividers */
hr {
    border-color: #e2e8f0;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HEADER
# ==================================================

col1, col2 = st.columns([0.6, 5])

with col1:
    st.markdown("# 🏥")

with col2:
    st.markdown("## FuzzyCare")
    st.caption("Smart Healthcare · Mamdani Fuzzy Inference System")

st.divider()


# ==================================================
# NAVIGATION
# ==================================================

page = st.radio(
    "Navigation",
    [
        "Dashboard",
        "New Assessment",
        "Patient History",
        "Fuzzy Logic"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.caption("PATIENT HEALTH RISK ASSESSMENT")

    st.title("Dashboard")

    st.write(
        "Health risk assessment using Mamdani Fuzzy Inference System."
    )

    history = st.session_state.history

    total = len(history)

    low = sum(
        p["Category"] == "Low Risk" for p in history
    )

    moderate = sum(
        p["Category"] == "Moderate Risk" for p in history
    )

    high = sum(
        p["Category"] == "High Risk" for p in history
    )

    # SUMMARY CARDS

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Assessments", total)
    c2.metric("Low Risk", low)
    c3.metric("Moderate Risk", moderate)
    c4.metric("High Risk", high)

    st.write("")

    left, right = st.columns(2)

    # RISK DISTRIBUTION

    with left:

        st.subheader("Risk Distribution")

        if total > 0:

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=[
                            "Low Risk",
                            "Moderate Risk",
                            "High Risk"
                        ],
                        values=[
                            low,
                            moderate,
                            high
                        ],
                        hole=0.55,
                        marker=dict(
                            colors=[
                                "#22a06b",
                                "#f0a52b",
                                "#e5484d"
                            ]
                        )
                    )
                ]
            )

            fig.update_layout(
                height=350,
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#263746"),
                margin=dict(t=30, b=30)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No assessments available yet.")

    # RECENT ASSESSMENTS

    with right:

        st.subheader("Recent Assessments")

        if total > 0:

            recent = history[-5:][::-1]

            st.dataframe(
                pd.DataFrame(recent),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Patient assessment records will appear here."
            )


# ==================================================
# NEW PATIENT ASSESSMENT
# ==================================================

elif page == "New Assessment":

    st.caption("MAMDANI FUZZY INFERENCE SYSTEM")

    st.title("New Patient Assessment")

    st.write(
        "Enter patient health parameters to calculate "
        "the health risk score."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        patient_id = st.text_input(
            "Patient ID",
            placeholder="Enter patient ID"
        )

        age = st.slider(
            "Age (years)",
            18,
            100,
            30
        )

        bmi = st.number_input(
            "Body Mass Index (BMI)",
            min_value=10.0,
            max_value=50.0,
            value=22.0,
            step=0.5
        )

    with col2:

        bp = st.number_input(
            "Systolic Blood Pressure (mmHg)",
            min_value=70,
            max_value=200,
            value=120
        )

        glucose = st.number_input(
            "Fasting Blood Glucose (mg/dL)",
            min_value=50,
            max_value=300,
            value=90
        )

    st.divider()

    if st.button(
        "🏥 Assess Health Risk",
        type="primary",
        use_container_width=True
    ):

        if not patient_id.strip():

            st.warning("Please enter Patient ID.")

        elif any(
            p["Patient ID"] == patient_id.strip()
            for p in st.session_state.history
        ):

            st.warning(
                "This Patient ID already exists in assessment history."
            )

        else:

            try:

                score, category = assess_health(
                    age,
                    bmi,
                    bp,
                    glucose
                )

                # SAVE PATIENT RECORD

                record = {
                    "Patient ID": patient_id.strip(),
                    "Date": datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    ),
                    "Age": age,
                    "BMI": bmi,
                    "BP": bp,
                    "Glucose": glucose,
                    "Risk Score": score,
                    "Category": category
                }

                st.session_state.history.append(record)

                st.success(
                    "Assessment completed successfully!"
                )

                st.divider()

                # RESULTS

                st.header("Assessment Results")

                result1, result2 = st.columns(2)

                result1.metric(
                    "Health Risk Score",
                    f"{score:.2f}/100"
                )

                result2.metric(
                    "Risk Category",
                    category
                )

                # GAUGE CHART

                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=score,
                        title={
                            "text": "Health Risk Score"
                        },
                        number={
                            "suffix": "/100"
                        },
                        gauge={
                            "axis": {
                                "range": [0, 100]
                            },
                            "bar": {
                                "color": "#009688"
                            },
                            "steps": [
                                {
                                    "range": [0, 35],
                                    "color": "#b7e4c7"
                                },
                                {
                                    "range": [35, 65],
                                    "color": "#ffe5a0"
                                },
                                {
                                    "range": [65, 100],
                                    "color": "#ffb3b3"
                                }
                            ]
                        }
                    )
                )

                fig.update_layout(
                    height=350,
                    paper_bgcolor="#ffffff",
                    font=dict(color="#263746")
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # RISK DESCRIPTION

                if category == "Low Risk":

                    st.success(
                        "The fuzzy system indicates a low health risk level."
                    )

                elif category == "Moderate Risk":

                    st.warning(
                        "The fuzzy system indicates a moderate health risk level."
                    )

                else:

                    st.error(
                        "The fuzzy system indicates a high health risk level."
                    )

                st.caption(
                    "Educational prototype only. "
                    "Results are not a medical diagnosis."
                )

            except Exception as e:

                st.error(
                    f"Assessment error: {e}"
                )


# ==================================================
# PATIENT HISTORY
# ==================================================

elif page == "Patient History":

    st.caption("PATIENT RECORDS")

    st.title("Patient History")

    history = st.session_state.history

    if history:

        df = pd.DataFrame(history)

        search = st.text_input(
            "Search Patient ID"
        )

        if search:

            df = df[
                df["Patient ID"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Patient Records (CSV)",
            csv,
            "FuzzyCare_Patient_History.csv",
            "text/csv"
        )

    else:

        st.info(
            "No patient records available. "
            "Complete a new assessment first."
        )


# ==================================================
# FUZZY LOGIC
# ==================================================

elif page == "Fuzzy Logic":

    st.caption("COMPUTATIONAL INTELLIGENCE")

    st.title("Mamdani Fuzzy Inference System")

    st.write(
        "FuzzyCare uses a Mamdani Fuzzy Inference System "
        "to assess patient health risk based on four input parameters."
    )

    st.divider()

    st.subheader("1. Input Variables")

    st.write("""
    The system considers four input parameters:

    - **Age:** Young, Middle-aged, Old
    - **BMI:** Low, Normal, High
    - **Blood Pressure:** Normal, Elevated, High
    - **Glucose:** Normal, Elevated, High
    """)

    st.subheader("2. Fuzzification")

    st.write("""
    Crisp input values are converted into fuzzy membership
    degrees using triangular and trapezoidal membership functions.
    """)

    st.subheader("3. Fuzzy Rule Evaluation")

    st.write("""
    "The system contains 12 manually designed IF-THEN fuzzy rules."

    Example:

    IF Age is Old AND BMI is High
    AND Blood Pressure is High
    AND Glucose is High

    THEN Health Risk is High.
    """)

    st.subheader("4. Aggregation")

    st.write("""
    The outputs of activated fuzzy rules are combined
    using the Maximum aggregation operator.
    """)

    st.subheader("5. Defuzzification")

    st.write("""
    The Centroid method converts the aggregated fuzzy output
    into a crisp numerical health risk score ranging from 0 to 100.
    """)

    st.divider()

    st.subheader("System Configuration")

    st.table({
        "Component": [
            "Fuzzy Model",
            "Input Variables",
            "Output Variable",
            "Membership Functions",
            "Rule Base",
            "AND Operator",
            "Aggregation",
            "Defuzzification"
        ],
        "Implementation": [
            "Mamdani FIS",
            "4",
            "Health Risk",
            "Triangular and Trapezoidal",
            "12 Rules",
            "Minimum",
            "Maximum",
            "Centroid"
        ]
    })


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "FuzzyCare | Smart Healthcare - Mamdani Fuzzy Inference System"
)