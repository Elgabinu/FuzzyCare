import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from itertools import product

# INPUT VARIABLES

age = ctrl.Antecedent(np.arange(18, 101, 1), 'age')
bmi = ctrl.Antecedent(np.arange(10, 51, 1), 'bmi')
bp = ctrl.Antecedent(np.arange(70, 201, 1), 'bp')
glucose = ctrl.Antecedent(np.arange(50, 301, 1), 'glucose')

# OUTPUT VARIABLE

risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk')

# MEMBERSHIP FUNCTIONS

# Age
age['young'] = fuzz.trapmf(age.universe, [18, 18, 30, 40])
age['middle'] = fuzz.trimf(age.universe, [30, 50, 70])
age['old'] = fuzz.trapmf(age.universe, [60, 75, 100, 100])

# BMI
bmi['low'] = fuzz.trapmf(bmi.universe, [10, 10, 16, 18.5])
bmi['normal'] = fuzz.trimf(bmi.universe, [18, 21.5, 25])
bmi['high'] = fuzz.trapmf(bmi.universe, [24, 30, 50, 50])

# Blood Pressure
bp['normal'] = fuzz.trapmf(bp.universe, [70, 70, 90, 120])
bp['elevated'] = fuzz.trimf(bp.universe, [110, 130, 140])
bp['high'] = fuzz.trapmf(bp.universe, [130, 150, 200, 200])

# Glucose
glucose['normal'] = fuzz.trapmf(
    glucose.universe, [50, 50, 70, 100]
)
glucose['elevated'] = fuzz.trimf(
    glucose.universe, [90, 110, 125]
)
glucose['high'] = fuzz.trapmf(
    glucose.universe, [115, 150, 300, 300]
)

# OUTPUT MEMBERSHIP FUNCTIONS

risk['low'] = fuzz.trapmf(risk.universe, [0, 0, 20, 40])
risk['moderate'] = fuzz.trimf(risk.universe, [25, 50, 75])
risk['high'] = fuzz.trapmf(risk.universe, [60, 80, 100, 100])

# FUZZY RULE BASE

# ==========================================
# FUZZY RULE BASE - 12 RULES
# ==========================================

rules = [

    # LOW RISK RULES

    ctrl.Rule(
        age['young'] & bmi['normal'] &
        bp['normal'] & glucose['normal'],
        risk['low']
    ),

    ctrl.Rule(
        age['young'] & bmi['high'] &
        bp['normal'] & glucose['normal'],
        risk['low']
    ),

    # MODERATE RISK RULES

    ctrl.Rule(
        age['middle'] & bmi['normal'] &
        bp['elevated'] & glucose['normal'],
        risk['moderate']
    ),

    ctrl.Rule(
        age['middle'] & bmi['high'] &
        bp['normal'] & glucose['elevated'],
        risk['moderate']
    ),

    ctrl.Rule(
        age['old'] & bmi['normal'] &
        bp['normal'] & glucose['normal'],
        risk['moderate']
    ),

    # HIGH RISK RULES

    ctrl.Rule(
        age['old'] & bmi['high'] &
        bp['elevated'] & glucose['normal'],
        risk['high']
    ),

    ctrl.Rule(
        age['young'] & bmi['normal'] &
        bp['high'] & glucose['high'],
        risk['high']
    ),

    ctrl.Rule(
        age['middle'] & bmi['normal'] &
        bp['high'] & glucose['elevated'],
        risk['high']
    ),

    ctrl.Rule(
        age['middle'] & bmi['high'] &
        bp['elevated'] & glucose['high'],
        risk['high']
    ),

    ctrl.Rule(
        age['old'] & bmi['normal'] &
        bp['elevated'] & glucose['high'],
        risk['high']
    ),

    ctrl.Rule(
        age['old'] & bmi['high'] &
        bp['high'] & glucose['elevated'],
        risk['high']
    ),

    ctrl.Rule(
        age['old'] & bmi['high'] &
        bp['high'] & glucose['high'],
        risk['high']
    )

]

# CONTROL SYSTEM

system = ctrl.ControlSystem(rules)


# ==========================================
# HEALTH RISK ASSESSMENT
# ==========================================

def assess_health(age_value, bmi_value, bp_value, glucose_value):

    simulation = ctrl.ControlSystemSimulation(system)

    simulation.input['age'] = age_value
    simulation.input['bmi'] = bmi_value
    simulation.input['bp'] = bp_value
    simulation.input['glucose'] = glucose_value

    simulation.compute()

    score = simulation.output['risk']

    if score < 35:
        category = "Low Risk"

    elif score < 65:
        category = "Moderate Risk"

    else:
        category = "High Risk"

    return round(score, 2), category

