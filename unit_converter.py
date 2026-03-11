#!/usr/bin/env python3

"""
Simple CLI tool to convert between metric and imperial units.

Supported categories and units:
  - length: m, km, ft, in, mi
  - weight: kg, g, lb, oz
  - temperature: c, f
  - volume: l, ml, gal, fl_oz

Examples:
  python unit_converter.py length --from m --to ft --value 3
  python unit_converter.py weight --from kg --to lb --value 5
  python unit_converter.py temperature --from c --to f --value 20
"""

import argparse
from typing import Callable, Dict, Tuple


class ConversionError(Exception):
    pass


def length_converter(from_unit: str, to_unit: str, value: float) -> float:
    # Base unit: meter
    to_meter = {
        "m": 1.0,
        "km": 1000.0,
        "ft": 0.3048,
        "in": 0.0254,
        "mi": 1609.344,
    }
    if from_unit not in to_meter or to_unit not in to_meter:
        raise ConversionError(f"Unsupported length units: {from_unit} -> {to_unit}")
    meters = value * to_meter[from_unit]
    return meters / to_meter[to_unit]


def weight_converter(from_unit: str, to_unit: str, value: float) -> float:
    # Base unit: kilogram
    to_kg = {
        "kg": 1.0,
        "g": 0.001,
        "lb": 0.45359237,
        "oz": 0.028349523125,
    }
    if from_unit not in to_kg or to_unit not in to_kg:
        raise ConversionError(f"Unsupported weight units: {from_unit} -> {to_unit}")
    kg = value * to_kg[from_unit]
    return kg / to_kg[to_unit]


def temperature_converter(from_unit: str, to_unit: str, value: float) -> float:
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit == to_unit:
        return value

    if from_unit == "c" and to_unit == "f":
        return (value * 9.0 / 5.0) + 32.0
    if from_unit == "f" and to_unit == "c":
        return (value - 32.0) * 5.0 / 9.0

    raise ConversionError(f"Unsupported temperature conversion: {from_unit} -> {to_unit}")


def volume_converter(from_unit: str, to_unit: str, value: float) -> float:
    # Base unit: liter
    to_liter = {
        "l": 1.0,
        "ml": 0.001,
        "gal": 3.785411784,  # US gallon
        "fl_oz": 0.0295735295625,  # US fluid ounce
    }
    if from_unit not in to_liter or to_unit not in to_liter:
        raise ConversionError(f"Unsupported volume units: {from_unit} -> {to_unit}")
    liters = value * to_liter[from_unit]
    return liters / to_liter[to_unit]


CONVERTERS: Dict[str, Tuple[Callable[[str, str, float], float], Tuple[str, ...]]] = {
    "length": (length_converter, ("m", "km", "ft", "in", "mi")),
    "weight": (weight_converter, ("kg", "g", "lb", "oz")),
    "temperature": (temperature_converter, ("c", "f")),
    "volume": (volume_converter, ("l", "ml", "gal", "fl_oz")),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert between metric and imperial units."
    )
    parser.add_argument(
        "category",
        choices=sorted(CONVERTERS.keys()),
        help="Type of quantity to convert",
    )
    parser.add_argument(
        "--from",
        dest="from_unit",
        required=True,
        help="Source unit (e.g. m, ft, kg, lb, c, f)",
    )
    parser.add_argument(
        "--to",
        dest="to_unit",
        required=True,
        help="Target unit (e.g. ft, m, lb, kg, f, c)",
    )
    parser.add_argument(
        "--value",
        type=float,
        required=True,
        help="Numeric value to convert",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    category = args.category
    from_unit = args.from_unit
    to_unit = args.to_unit
    value = args.value

    converter, supported_units = CONVERTERS[category]

    if from_unit not in supported_units or to_unit not in supported_units:
        raise SystemExit(
            f"Unsupported units for {category}. "
            f"Supported: {', '.join(supported_units)}"
        )

    try:
        result = converter(from_unit, to_unit, value)
    except ConversionError as exc:
        raise SystemExit(str(exc))

    print(f"{value} {from_unit} = {result} {to_unit}")


if __name__ == "__main__":
    main()

