from dataclasses import dataclass
from datetime import datetime, timedelta
from random import randint, random

import pandas as pd


@dataclass
class SPSSVariable:
    name: str
    label: str
    type: int
    format: str | tuple[int, int, int]
    measure_level: int | str
    alignment: int | str
    width: int = randint(1, 200)
    role: int | str = randint(0, 7)
    value_labels: dict[float | int | str, str] | None = None
    missing_values: dict[str, int | str] | None = None


file_attributes = {
    "TestAttr1": "This is a test attribute value",
    "test_attr_2": "number 2",
    "three": 3,
}


variables = [
    SPSSVariable(
        name="var_id",
        label="Variable ID",
        type=0,
        format=(5, 8, 0),
        measure_level="ordinal",
        alignment="left",
    ),
    SPSSVariable(
        name="numeric_var",
        label="Numeric Variable",
        type=0,
        format=(5, 8, 2),
        measure_level="scale",
        alignment="right",
        missing_values={"values": [-1, 0, 999]},
    ),
    SPSSVariable(
        name="numeric_var_2",
        label="Numeric Variable",
        type=0,
        format=(5, 8, 2),
        measure_level="scale",
        alignment="right",
        missing_values={"lo": float("-inf"), "hi": 0, "values": [9999]},
    ),
    SPSSVariable(
        name="date_var",
        label="Datetime Variable",
        type=0,
        format="DATETIME20",
        measure_level=3,
        alignment=1,
    ),
    SPSSVariable(
        name="string_var",
        label="String Variable",
        type=100,
        format="A100",
        measure_level=1,
        alignment=0,
    ),
    SPSSVariable(
        name="long_string_var",
        label="Long String",
        type=1000,
        format=(1, 1000, 0),
        measure_level="nominal",
        alignment=0,
    ),
    SPSSVariable(
        name="has_apple",
        label="Apple",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment=2,
        value_labels={1: "Yes", 0: "No"},
    ),
    SPSSVariable(
        name="has_orange",
        label="Orange",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment="center",
        value_labels={1: "Yes", 0: "No"},
    ),
    SPSSVariable(
        name="has_banana",
        label="Banana",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment="center",
        value_labels={1: "Yes", 0: "No"},
    ),
    SPSSVariable(
        name="fruit_1",
        label="Fruit #1",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment=0,
        value_labels={1: "Apple", 2: "Orange", 3: "Banana"},
    ),
    SPSSVariable(
        name="fruit_2",
        label="Fruit #2",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment="left",
        value_labels={1: "Apple", 2: "Orange", 3: "Banana"},
    ),
    SPSSVariable(
        name="fruit_3",
        label="Fruit #3",
        type=0,
        format="F2.0",
        measure_level=1,
        alignment="left",
        value_labels={1: "Apple", 2: "Orange", 3: "Banana"},
    ),
]

var_types = {v.name: v.type for v in variables}
var_formats = {v.name: v.format for v in variables}
var_measure_levels = {v.name: v.measure_level for v in variables}
var_alignments = {v.name: v.alignment for v in variables}
var_widths = {v.name: v.width for v in variables}
var_labels = {v.name: v.label for v in variables}
var_roles = {v.name: v.role for v in variables}
var_value_labels = {v.name: v.value_labels for v in variables if v.value_labels}
var_missing_values = {v.name: v.missing_values for v in variables if v.missing_values}

mrsets = {
    "$fruits_md": {
        "label": "Fruits (MD)",
        "is_dichotomy": True,
        "counted_value": 1,
        "variable_list": ["has_apple", "has_orange", "has_banana"],
    },
    "$fruits_mc": {
        "label": "Fruits (MC)",
        "is_dichotomy": False,
        "variable_list": ["fruit_1", "fruit_2", "fruit_3"],
    },
}


metadata = {
    "file_attributes": file_attributes,
    "var_types": var_types,
    "var_formats": var_formats,
    "var_measure_levels": var_measure_levels,
    "var_alignments": var_alignments,
    "var_widths": var_widths,
    "var_labels": var_labels,
    "var_roles": var_roles,
    "var_value_labels": var_value_labels,
    "var_missing_values": var_missing_values,
    "mrsets": mrsets,
}

words = [
    ["Black", "White", "Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"],
    ["Dog", "Cat", "Horse", "Cow", "Lion", "Tiger", "Elephant"],
    ["Run", "Walk", "Gallop", "Stand", "Sit", "Sleep"],
]


records = []


for i in range(10):
    records.append(
        (
            i + 1,
            randint(-5000, 10000) * random(),
            randint(-5000, 10000) * random(),
            datetime.now() + timedelta(days=randint(-1000, 1000)),
            words[0][randint(0, len(words[0]) - 1)],
            (
                " ".join(
                    words[j][randint(0, len(words[j]) - 1)] for j in range(len(words))
                )
                + " "
            )
            * randint(0, 20),
            randint(0, 1),
            randint(0, 1),
            randint(0, 1),
            randint(1, 3),
            randint(1, 3) if random() > 0.25 else None,
            randint(1, 3) if random() > 0.5 else None,
        )
    )

df = pd.DataFrame(records, columns=[v.name for v in variables])
