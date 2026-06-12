"""CrossHair-checkable contracts for protected clinical calculations."""

from pharmacy_app.logic import (
    calc_bsa_mosteller,
    calc_crcl_cockcroft_gault,
    calc_days_supply_logic,
)


def bsa_contract(height_cm: int, weight_kg: int) -> float:
    """
    pre: 1 <= height_cm <= 300
    pre: 1 <= weight_kg <= 500
    post: _ > 0.0
    """
    return calc_bsa_mosteller(height_cm, weight_kg)


def crcl_contract(age: int, weight_kg: int, serum_creatinine: int) -> float:
    """
    pre: 1 <= age <= 130
    pre: 1 <= weight_kg <= 500
    pre: 1 <= serum_creatinine <= 30
    post: _ >= 0.0
    """
    return calc_crcl_cockcroft_gault(age, weight_kg, serum_creatinine)


def days_supply_contract(quantity: int, units_per_day: int) -> int:
    """
    pre: 1 <= quantity <= 1000000
    pre: 1 <= units_per_day <= 1000000
    pre: quantity / units_per_day <= 3650
    post: 0 <= _ <= 3650
    """
    return calc_days_supply_logic(quantity, units_per_day)
