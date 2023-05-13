import logging
import subprocess


def parse_xboxdrv_input(controller_input_str):
    # Example input string:
    # "X1:   128 Y1:   128  X2:   128 Y2:   128  du:0 dd:0 dl:0 dr:0  back:0 guide:0 start:0  TL:0 TR:0  A:0 B:0 X:0 Y:0  LB:0 RB:0  LT:255 RT:  0"

    if controller_input_str[0:3] != "X1:":
        return None

    controller_inputs = dict()

    try:
        iter_count = 0
        while True:
            # Parse field name
            # controller_input_str = "X1:   128 Y1:   128"
            colon_index = controller_input_str.find(":")
            field_name = controller_input_str[:colon_index]
            controller_input_str = controller_input_str[colon_index + 1 :]

            # Parse field value
            # controller_input_str = "   128 Y1:   128"
            while controller_input_str.find(" ") == 0:
                controller_input_str = controller_input_str[1:]
            value_end_index = controller_input_str.find(" ")
            if value_end_index < 0:
                value_end_index = len(controller_input_str)
            field_value = int(controller_input_str[:value_end_index])
            controller_inputs[field_name] = field_value
            controller_input_str = controller_input_str[value_end_index:]
            if len(controller_input_str) == 0:
                # controller_input_str = ""
                break

            # Remove remaining spaces
            # controller_input_str = " Y1:   128"
            while controller_input_str.find(" ") == 0:
                controller_input_str = controller_input_str[1:]
            # controller_input_str = "Y1:   128"

            iter_count += 1
            if iter_count > 100:
                raise Exception(
                    "Too many iterations parsing xboxdrv string, somthing has gone wrong"
                )
    except Exception as e:
        logging.error("Error parsing xboxdrv input string")
        logging.error(e)
        return None

    return controller_inputs


CONTROLLER_FIELDS = {
    "X1": {
        "description": "Left stick X axis",
        "min": -32768,
        "max": 32768,
    },
    "Y1": {
        "description": "Left stick Y axis",
        "min": -32768,
        "max": 32768,
    },
    "X2": {
        "description": "Right stick X axis",
        "min": -32768,
        "max": 32768,
    },
    "Y2": {
        "description": "Right stick Y axis",
        "min": -32768,
        "max": 32768,
    },
    "du": {
        "description": "D-pad up",
        "min": 0,
        "max": 1,
    },
    "dd": {
        "description": "D-pad down",
        "min": 0,
        "max": 1,
    },
    "dl": {
        "description": "D-pad left",
        "min": 0,
        "max": 1,
    },
    "dr": {
        "description": "D-pad right",
        "min": 0,
        "max": 1,
    },
    "back": {
        "description": "Back button",
        "min": 0,
        "max": 1,
    },
    "guide": {
        "description": "Guide button",
        "min": 0,
        "max": 1,
    },
    "start": {
        "description": "Start button",
        "min": 0,
        "max": 1,
    },
    "A": {
        "description": "A button",
        "min": 0,
        "max": 1,
    },
    "B": {
        "description": "B button",
        "min": 0,
        "max": 1,
    },
    "X": {
        "description": "X button",
        "min": 0,
        "max": 1,
    },
    "Y": {
        "description": "Y button",
        "min": 0,
        "max": 1,
    },
    "LB": {
        "description": "Left Bumper",
        "min": 0,
        "max": 1,
    },
    "RB": {
        "description": "Right Bumper",
        "min": 0,
        "max": 1,
    },
    "LT": {
        "description": "Left Trigger",
        "min": 0,
        "max": 255,
    },
    "RT": {
        "description": "Right Trigger",
        "min": 0,
        "max": 255,
    },
}
# 'TL' and 'TR' are not included


def normalize_xboxdrv_input(controller_inputs):
    normalized_inputs = dict()
    for field_name, field_value in controller_inputs.items():
        if field_name not in CONTROLLER_FIELDS:
            continue
        field_info = CONTROLLER_FIELDS[field_name]
        field_value_normalized = (float(field_value) - field_info["min"]) / (
            field_info["max"] - field_info["min"]
        )
        normalized_inputs[field_name] = field_value_normalized
    return normalized_inputs


def f710():
    logging.info("Starting F710 controller process")
    proc = subprocess.Popen(
        ["sudo", "xboxdrv", "--detach-kernel-driver"], stdout=subprocess.PIPE
    )
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        controller_inputs_str = line.decode("utf-8")
        controller_inputs = parse_xboxdrv_input(controller_inputs_str)

        if controller_inputs is None:
            continue

        normalized_inputs = normalize_xboxdrv_input(controller_inputs)

        print(normalized_inputs)
