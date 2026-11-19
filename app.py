import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from fuzzy_system import (
    assess_health,
    risk_universe,
    risk_mf,
    rule_definitions
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FuzzyCare",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f9fc;
    color: #263746;
}

h1, h2, h3 {
    color: #173b4a;
}

div.stButton > button {
    background-color: #087f8c;
    color: white;
    border-radius: 8px;
    border: none;
}

div.stButton > button:hover {
    background-color: #066b76;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.title("🏥 FuzzyCare")

st.caption(
    "Smart Healthcare | Patient Health Risk Assessment "
    "Using Mamdani Fuzzy Inference System"
)

st.divider()


# ==========================================
# NAVIGATION
# ==========================================

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


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.header("Dashboard")

    history = st.session_state.history

    total = len(history)

    low = sum(
        x["Category"] == "Low Risk"
        for x in history
    )

    moderate = sum(
        x["Category"] == "Moderate Risk"
        for x in history
    )

    high = sum(
        x["Category"] == "High Risk"
        for x in history
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Assessments", total)

    c2.metric("Low Risk", low)

    c3.metric("Moderate Risk", moderate)

    c4.metric("High Risk", high)

    st.divider()

    if history:

        chart_data = pd.DataFrame({

            "Category": [
                "Low Risk",
                "Moderate Risk",
                "High Risk"
            ],

            "Count": [
                low,
                moderate,
                high
            ]

        })

        st.subheader("Risk Distribution")

        fig = px.pie(

            chart_data,

            names="Category",

            values="Count",

            hole=0.5

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Recent Assessments")

        df = pd.DataFrame(history).drop(
            columns=["Activated Rules"],
            errors="ignore"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "No assessments available. Create a new assessment."
        )


# ==========================================
# NEW ASSESSMENT
# ==========================================

elif page == "New Assessment":

    st.header("Patient Health Assessment")

    st.write(
        "Enter the patient's health information."
    )

    with st.form("assessment_form"):

        col1, col2 = st.columns(2)

        with col1:

            patient_id = st.text_input(
                "Patient ID",
                value="1"
            )

            age_value = st.number_input(
                "Age (Years)",
                min_value=18,
                max_value=100,
                value=48
            )

            bmi_value = st.number_input(
                "BMI",
                min_value=10.0,
                max_value=50.0,
                value=24.8,
                step=0.1
            )

        with col2:

            bp_value = st.number_input(
                "Systolic Blood Pressure (mmHg)",
                min_value=70,
                max_value=200,
                value=120
            )

            glucose_value = st.number_input(
                "Blood Glucose (mg/dL)",
                min_value=50,
                max_value=300,
                value=100
            )

        submitted = st.form_submit_button(
            "Assess Health",
            use_container_width=True
        )


    if submitted:

        if not patient_id.strip():

            st.error("Please enter a Patient ID.")

        else:

            try:

                result = assess_health(

                    age_value,

                    bmi_value,

                    bp_value,

                    glucose_value

                )


                score = result["score"]

                category = result["category"]

                activated_rules = result["activated_rules"]


                # ==================================
                # SAVE RECORD
                # ==================================

                record = {

                    "Patient ID": patient_id,

                    "Age": age_value,

                    "BMI": bmi_value,

                    "BP": bp_value,

                    "Glucose": glucose_value,

                    "Risk Score": score,

                    "Category": category,

                    "Activated Rules": activated_rules

                }

                st.session_state.history.append(record)


                # ==================================
                # ASSESSMENT RESULT
                # ==================================

                st.divider()

                st.subheader("Assessment Result")

                c1, c2 = st.columns(2)

                c1.metric(
                    "Risk Score",
                    f"{score} / 100"
                )

                c2.metric(
                    "Risk Category",
                    category
                )


                # Gauge chart

                gauge = go.Figure(

                    go.Indicator(

                        mode="gauge+number",

                        value=score,

                        title={
                            "text": "Health Risk Score"
                        },

                        gauge={

                            "axis": {
                                "range": [0, 100]
                            },

                            "steps": [

                                {
                                    "range": [0, 35],
                                    "color": "#b8e6d0"
                                },

                                {
                                    "range": [35, 65],
                                    "color": "#f9e5a5"
                                },

                                {
                                    "range": [65, 100],
                                    "color": "#f3b6b6"
                                }

                            ]

                        }

                    )

                )

                st.plotly_chart(
                    gauge,
                    use_container_width=True
                )


                # ==================================
                # FUZZIFICATION RESULTS
                # ==================================

                st.divider()

                st.subheader("1. Fuzzification Results")

                membership_df = pd.DataFrame({

                    "Parameter": [
                        "Age",
                        "BMI",
                        "Blood Pressure",
                        "Blood Glucose"
                    ],

                    "Membership Values": [

                        str(result["age_membership"]),

                        str(result["bmi_membership"]),

                        str(result["bp_membership"]),

                        str(result["glucose_membership"])

                    ]

                })

                st.dataframe(
                    membership_df,
                    use_container_width=True,
                    hide_index=True
                )


                # ==================================
                # ACTIVATED RULES
                # ==================================

                st.divider()

                st.subheader("2. Activated IF–THEN Rules")

                st.write(
                    "The following rules were activated "
                    "for the given patient inputs."
                )

                rule_df = pd.DataFrame(
                    activated_rules
                )

                rule_df["IF–THEN Rule"] = rule_df.apply(

                    lambda row: (
                        f"IF {row['Condition']}, "
                        f"THEN Risk is {row['Output']}"
                    ),

                    axis=1

                )

                st.dataframe(

                    rule_df[
                        [
                            "Rule",
                            "IF–THEN Rule",
                            "Firing Strength"
                        ]
                    ],

                    use_container_width=True,

                    hide_index=True

                )


                # ==================================
                # RULE ACTIVATION GRAPH
                # ==================================

                st.subheader("3. Rule Activation Graph")

                fig_rules = px.bar(

                    rule_df,

                    x="Rule",

                    y="Firing Strength",

                    color="Output",

                    text="Firing Strength",

                    title="Activated Rule Firing Strengths"

                )

                fig_rules.update_layout(

                    xaxis_title="Activated Rules",

                    yaxis_title="Firing Strength (0–1)",

                    yaxis_range=[0, 1]

                )

                st.plotly_chart(
                    fig_rules,
                    use_container_width=True
                )


                # ==================================
                # OUTPUT MEMBERSHIP GRAPH
                # ==================================

                st.divider()

                st.subheader(
                    "4. Risk Output Membership Functions"
                )

                fig_risk = go.Figure()

                for term in ["low", "moderate", "high"]:

                    fig_risk.add_trace(

                        go.Scatter(

                            x=risk_universe,

                            y=risk_mf[term],

                            mode="lines",

                            name=term.title()

                        )

                    )


                # Final score marker

                fig_risk.add_vline(

                    x=score,

                    line_dash="dash",

                    annotation_text=f"Final Score: {score}"

                )


                fig_risk.update_layout(

                    title="Risk Membership Functions",

                    xaxis_title="Risk Score",

                    yaxis_title="Membership Degree",

                    yaxis_range=[0, 1]

                )

                st.plotly_chart(
                    fig_risk,
                    use_container_width=True
                )


                # ==================================
                # AGGREGATED OUTPUT GRAPH
                # ==================================

                st.subheader(
                    "5. Aggregated Fuzzy Output"
                )

                fig_agg = go.Figure()

                fig_agg.add_trace(

                    go.Scatter(

                        x=risk_universe,

                        y=result["aggregated_output"],

                        mode="lines",

                        fill="tozeroy",

                        name="Aggregated Output"

                    )

                )

                fig_agg.add_vline(

                    x=score,

                    line_dash="dash",

                    annotation_text=f"Centroid: {score}"

                )

                fig_agg.update_layout(

                    title="Aggregated Output After Rule Evaluation",

                    xaxis_title="Risk Score",

                    yaxis_title="Membership Degree",

                    yaxis_range=[0, 1]

                )

                st.plotly_chart(
                    fig_agg,
                    use_container_width=True
                )


                st.success(
                    f"Assessment completed: {category}"
                )

                st.caption(
                    "Educational prototype only. "
                    "This result is not a medical diagnosis."
                )


            except Exception as e:

                st.error(
                    f"Assessment could not be completed: {e}"
                )


# ==========================================
# PATIENT HISTORY
# ==========================================

elif page == "Patient History":

    st.header("Patient Assessment History")

    history = st.session_state.history

    if history:

        df = pd.DataFrame(history).drop(

            columns=["Activated Rules"],

            errors="ignore"

        )

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

        st.download_button(

            "Download History CSV",

            df.to_csv(index=False),

            file_name="fuzzycare_history.csv",

            mime="text/csv"

        )

    else:

        st.info("No patient records available.")


# ==========================================
# FUZZY LOGIC
# ==========================================

elif page == "Fuzzy Logic":

    st.header("Mamdani Fuzzy Inference System")

    st.write(
        "FuzzyCare uses a Mamdani Fuzzy Inference System "
        "to estimate patient health risk."
    )

    st.subheader("System Workflow")

    st.markdown("""
    1. **Input Collection:** Age, BMI, Blood Pressure and Glucose.
    2. **Fuzzification:** Converts numerical inputs into membership degrees.
    3. **Rule Evaluation:** Evaluates 81 IF–THEN rules.
    4. **Implication:** Clips the output membership function using the rule firing strength.
    5. **Aggregation:** Combines rule outputs using the maximum operator.
    6. **Defuzzification:** Uses the centroid method to calculate a crisp score.
    7. **Classification:** Classifies the score as Low, Moderate or High Risk.
    """)

    st.divider()

    st.subheader("Input Variables")

    st.dataframe(

        pd.DataFrame({

            "Input": [
                "Age",
                "BMI",
                "Systolic BP",
                "Blood Glucose"
            ],

            "Range": [
                "18–100 years",
                "10–50",
                "70–200 mmHg",
                "50–300 mg/dL"
            ],

            "Categories": [
                "Young, Middle, Old",
                "Low, Normal, High",
                "Normal, Elevated, High",
                "Normal, Elevated, High"
            ]

        }),

        use_container_width=True,

        hide_index=True

    )

    st.subheader("Output Variable")

    st.write(
        "Risk score ranges from 0 to 100."
    )

    st.write(
        "Output categories: Low, Moderate and High."
    )

    st.subheader("Membership Functions")

    st.write(
        "Triangular and trapezoidal membership functions "
        "are used."
    )

    st.subheader("Rule Base")

    st.write(
        f"The system contains {len(rule_definitions)} "
        "automatically generated IF–THEN rules."
    )

    st.dataframe(

        pd.DataFrame(rule_definitions),

        use_container_width=True,

        hide_index=True

    )

    st.info(
        "The rule-output mapping uses illustrative severity "
        "weights for an academic prototype. It is not medically "
        "validated and should not be used for clinical decisions."
    )