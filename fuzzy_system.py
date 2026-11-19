import numpy as np
import skfuzzy as fuzz
from itertools import product


# ==========================================
# 1. DEFINE INPUT UNIVERSES
# ==========================================

age_universe = np.arange(18, 101, 1)
bmi_universe = np.arange(10, 51, 1)
bp_universe = np.arange(70, 201, 1)
glucose_universe = np.arange(50, 301, 1)

risk_universe = np.arange(0, 101, 1)


# ==========================================
# 2. DEFINE MEMBERSHIP FUNCTIONS
# ==========================================

# AGE

age_mf = {
    "young": fuzz.trapmf(
        age_universe, [18, 18, 30, 40]
    ),

    "middle": fuzz.trimf(
        age_universe, [30, 50, 70]
    ),

    "old": fuzz.trapmf(
        age_universe, [60, 75, 100, 100]
    )
}


# BMI

bmi_mf = {
    "low": fuzz.trapmf(
        bmi_universe, [10, 10, 16, 18.5]
    ),

    "normal": fuzz.trimf(
        bmi_universe, [18, 21.5, 25]
    ),

    "high": fuzz.trapmf(
        bmi_universe, [24, 30, 50, 50]
    )
}


# BLOOD PRESSURE

bp_mf = {
    "normal": fuzz.trapmf(
        bp_universe, [70, 70, 90, 120]
    ),

    "elevated": fuzz.trimf(
        bp_universe, [110, 130, 140]
    ),

    "high": fuzz.trapmf(
        bp_universe, [130, 150, 200, 200]
    )
}


# GLUCOSE

glucose_mf = {
    "normal": fuzz.trapmf(
        glucose_universe, [50, 50, 70, 100]
    ),

    "elevated": fuzz.trimf(
        glucose_universe, [90, 110, 125]
    ),

    "high": fuzz.trapmf(
        glucose_universe, [115, 150, 300, 300]
    )
}


# OUTPUT RISK

risk_mf = {
    "low": fuzz.trapmf(
        risk_universe, [0, 0, 20, 40]
    ),

    "moderate": fuzz.trimf(
        risk_universe, [25, 50, 75]
    ),

    "high": fuzz.trapmf(
        risk_universe, [60, 80, 100, 100]
    )
}


# ==========================================
# 3. DEFINE FUZZY CATEGORIES
# ==========================================

age_terms = ["young", "middle", "old"]

bmi_terms = ["low", "normal", "high"]

bp_terms = ["normal", "elevated", "high"]

glucose_terms = ["normal", "elevated", "high"]


# ==========================================
# 4. RULE OUTPUT SELECTION
# ==========================================

# Illustrative severity weights for this project.
# These are not medically validated weights.

age_severity = {
    "young": 0,
    "middle": 1,
    "old": 2
}

bmi_severity = {
    "low": 1,
    "normal": 0,
    "high": 1.5
}

bp_severity = {
    "normal": 0,
    "elevated": 1,
    "high": 2
}

glucose_severity = {
    "normal": 0,
    "elevated": 1,
    "high": 2
}


def get_rule_output(a, b, c, d):

    severity = (
        0.5 * age_severity[a]
        + 1.0 * bmi_severity[b]
        + 1.5 * bp_severity[c]
        + 1.5 * glucose_severity[d]
    )

    if severity <= 2:
        return "low"

    elif severity <= 5:
        return "moderate"

    else:
        return "high"


# ==========================================
# 5. GENERATE 81 FUZZY RULES
# ==========================================

rule_definitions = []

combinations = product(
    age_terms,
    bmi_terms,
    bp_terms,
    glucose_terms
)

for index, (a, b, c, d) in enumerate(
    combinations, start=1
):

    output = get_rule_output(a, b, c, d)

    rule_definitions.append({

        "Rule": f"R{index}",

        "Age": a,

        "BMI": b,

        "BP": c,

        "Glucose": d,

        "Output": output

    })


# ==========================================
# 6. FUZZIFICATION FUNCTION
# ==========================================

def calculate_membership(universe, membership_functions, value):

    result = {}

    for term, mf in membership_functions.items():

        degree = fuzz.interp_membership(
            universe,
            mf,
            value
        )

        result[term] = float(degree)

    return result


# ==========================================
# 7. MAIN ASSESSMENT FUNCTION
# ==========================================

def assess_health(
    age_value,
    bmi_value,
    bp_value,
    glucose_value
):

    # --------------------------------------
    # STEP 1: FUZZIFICATION
    # --------------------------------------

    age_membership = calculate_membership(
        age_universe,
        age_mf,
        age_value
    )

    bmi_membership = calculate_membership(
        bmi_universe,
        bmi_mf,
        bmi_value
    )

    bp_membership = calculate_membership(
        bp_universe,
        bp_mf,
        bp_value
    )

    glucose_membership = calculate_membership(
        glucose_universe,
        glucose_mf,
        glucose_value
    )


    # --------------------------------------
    # STEP 2: RULE EVALUATION
    # --------------------------------------

    activated_rules = []

    aggregated_output = np.zeros_like(
        risk_universe,
        dtype=float
    )


    for rule in rule_definitions:

        a = rule["Age"]
        b = rule["BMI"]
        c = rule["BP"]
        d = rule["Glucose"]

        output = rule["Output"]


        # AND operation using minimum

        strength = min(

            age_membership[a],

            bmi_membership[b],

            bp_membership[c],

            glucose_membership[d]

        )


        if strength > 0:

            activated_rules.append({

                "Rule": rule["Rule"],

                "Condition": (
                    f"Age is {a.title()} AND "
                    f"BMI is {b.title()} AND "
                    f"BP is {c.title()} AND "
                    f"Glucose is {d.title()}"
                ),

                "Output": output.title(),

                "Firing Strength": round(
                    strength, 4
                )

            })


            # ----------------------------------
            # STEP 3: IMPLICATION
            # ----------------------------------

            # Clip output membership function
            # using the rule firing strength

            clipped_output = np.fmin(

                strength,

                risk_mf[output]

            )


            # ----------------------------------
            # STEP 4: AGGREGATION
            # ----------------------------------

            # Combine all rule outputs using MAX

            aggregated_output = np.fmax(

                aggregated_output,

                clipped_output

            )


    # --------------------------------------
    # STEP 5: DEFUZZIFICATION
    # --------------------------------------

    if np.max(aggregated_output) == 0:

        raise ValueError(
            "No fuzzy output was generated."
        )

    score = fuzz.defuzz(

        risk_universe,

        aggregated_output,

        "centroid"

    )


    # --------------------------------------
    # STEP 6: RISK CLASSIFICATION
    # --------------------------------------

    if score < 35:

        category = "Low Risk"

    elif score < 65:

        category = "Moderate Risk"

    else:

        category = "High Risk"


    # --------------------------------------
    # RETURN RESULTS
    # --------------------------------------

    return {

        "score": round(float(score), 2),

        "category": category,

        "activated_rules": activated_rules,

        "age_membership": age_membership,

        "bmi_membership": bmi_membership,

        "bp_membership": bp_membership,

        "glucose_membership": glucose_membership,

        "aggregated_output": aggregated_output

    }