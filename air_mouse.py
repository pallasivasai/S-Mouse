import cv2

import mediapipe as mp

import pyautogui

import math

import time
import json
import os
import ctypes
import webbrowser





# ============================================================

# SAI AIR MOUSE

# ============================================================

#

# ☝️ INDEX FINGER ONLY

#       -> Mouse movement

#

# ✌️ INDEX + MIDDLE CLOSE

#       -> Left click

#

# ✌️ HOLD

#       -> Drag

#

# 👍 + MIDDLE

#       -> Right click

#

# ✌️ TWO FINGERS

#       -> Scroll

#

# ✋ OPEN PALM

#       -> Mouse STOP

#       -> App switching

#

# 🔒 Cursor locks ONLY during normal click.

# ============================================================





# ============================================================

# CAMERA SETTINGS

# ============================================================



CAMERA_INDEX = 0



CAMERA_WIDTH = 640

CAMERA_HEIGHT = 480



TARGET_FPS = 60



FRAME_REDUCTION = 50





# ============================================================

# CURSOR SETTINGS

# ============================================================



DEADZONE = 0.75



SMOOTH_ALPHA_SMALL = 0.10

SMOOTH_ALPHA_MEDIUM = 0.22

SMOOTH_ALPHA_FAST = 0.42





# ============================================================

# CLICK SETTINGS

# ============================================================



CLICK_START = 0.32



CLICK_RELEASE = 0.45



CLICK_CONFIRM_FRAMES = 2



CLICK_COOLDOWN = 0.25



DOUBLE_CLICK_WINDOW = 0.45



DRAG_HOLD_TIME = 0.70





# ============================================================

# RIGHT CLICK

# ============================================================



RIGHT_CLICK_THRESHOLD = 0.48





# ============================================================

# SCROLL

# ============================================================



SCROLL_DEADZONE = 8



SCROLL_MULTIPLIER = 0.12





# ============================================================

# APP SWITCHING

# ============================================================



APP_MIN_DISTANCE = 55



APP_MIN_SPEED = 120



APP_HORIZONTAL_RATIO = 1.35



APP_MAX_GESTURE_TIME = 1.10



APP_SWITCH_COOLDOWN = 0.65



APP_HISTORY_SIZE = 12
APP_CONFIRM_DISTANCE = 42
APP_RELEASE_DISTANCE = 24
APP_DIRECTION_STABILITY = 3
# ============================================================
# CUSTOM GESTURE LEARNING
# ============================================================

CUSTOM_GESTURE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sai_gestures.json"
)

CUSTOM_CAPTURE_FRAMES = 45
CUSTOM_MATCH_THRESHOLD = 0.145
CUSTOM_CONFIRM_FRAMES = 4
CUSTOM_RELEASE_FRAMES = 8
CUSTOM_TRIGGER_COOLDOWN = 1.25

CUSTOM_ACTIONS = {
    "1": "SCREENSHOT",
    "2": "PLAY_PAUSE",
    "3": "NEXT_TRACK",
    "4": "PREVIOUS_TRACK",
    "5": "SHOW_DESKTOP",
    "6": "CALCULATOR",
    "7": "OPEN_BROWSER"
}







# ============================================================

# PYAUTOGUI

# ============================================================



pyautogui.PAUSE = 0



pyautogui.FAILSAFE = True





# ============================================================

# MEDIAPIPE

# ============================================================



mp_hands = mp.solutions.hands

mp_draw = mp.solutions.drawing_utils





hands = mp_hands.Hands(

    static_image_mode=False,

    max_num_hands=1,

    model_complexity=0,

    min_detection_confidence=0.50,

    min_tracking_confidence=0.50

)





# ============================================================

# CAMERA

# ============================================================



cap = cv2.VideoCapture(

    CAMERA_INDEX,

    cv2.CAP_DSHOW

)





if not cap.isOpened():



    print("ERROR: Could not open camera.")



    raise SystemExit





cap.set(

    cv2.CAP_PROP_FRAME_WIDTH,

    CAMERA_WIDTH

)



cap.set(

    cv2.CAP_PROP_FRAME_HEIGHT,

    CAMERA_HEIGHT

)



cap.set(

    cv2.CAP_PROP_FPS,

    TARGET_FPS

)



cap.set(

    cv2.CAP_PROP_BUFFERSIZE,

    1

)





# ============================================================

# SCREEN

# ============================================================



screen_width, screen_height = pyautogui.size()



previous_mouse_x = screen_width / 2

previous_mouse_y = screen_height / 2





# ============================================================

# LEFT CLICK STATE

# ============================================================



left_gesture = False



click_confirm_counter = 0



dragging = False



gesture_started_at = None



last_click_time = 0



last_left_click_time = 0





# ============================================================

# CURSOR LOCK

# ============================================================



cursor_locked = False



locked_mouse_x = None

locked_mouse_y = None





# ============================================================

# RIGHT CLICK STATE

# ============================================================



right_gesture = False





# ============================================================

# SCROLL STATE

# ============================================================



previous_scroll_x = None

previous_scroll_y = None





# ============================================================

# APP SWITCH STATE

# ============================================================



app_history = []



app_gesture_active = False



app_gesture_start_time = None



app_start_x = None

app_start_y = None



app_switch_locked = False



last_app_switch_time = 0





# ============================================================

# STATUS

# ============================================================



gesture = "READY"





# ============================================================

# FPS

# ============================================================



previous_time = time.perf_counter()



fps = 0

# ============================================================
# CUSTOM GESTURE STATE
# ============================================================

custom_gestures = {}
learning_active = False
learning_phase = "idle"
learning_samples = []
learning_target_frames = CUSTOM_CAPTURE_FRAMES
learning_name = None
learning_template = None
learning_action = None

custom_match_count = 0
custom_release_count = 0
custom_trigger_locked = False
last_custom_trigger_time = 0
last_custom_name = ""







# ============================================================

# HELPER FUNCTIONS

# ============================================================



def distance(x1, y1, x2, y2):



    return math.hypot(

        x2 - x1,

        y2 - y1

    )





def clamp(value, minimum, maximum):



    return max(

        minimum,

        min(value, maximum)

    )





def clear_app_history():



    app_history.clear()







def load_custom_gestures():
    global custom_gestures

    try:
        if os.path.exists(CUSTOM_GESTURE_FILE):
            with open(CUSTOM_GESTURE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                custom_gestures = data
            else:
                custom_gestures = {}
        else:
            custom_gestures = {}

    except Exception:
        custom_gestures = {}


def save_custom_gestures():
    try:
        with open(CUSTOM_GESTURE_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_gestures, f, indent=2)
        return True
    except Exception:
        return False


def gesture_feature_vector(landmarks):
    """Normalize 21 landmarks around the wrist and palm scale."""
    wrist = landmarks[0]

    scale = math.sqrt(
        (landmarks[5].x - landmarks[17].x) ** 2 +
        (landmarks[5].y - landmarks[17].y) ** 2 +
        (landmarks[5].z - landmarks[17].z) ** 2
    )

    if scale < 1e-6:
        scale = 1.0

    vector = []

    for p in landmarks:
        vector.extend([
            (p.x - wrist.x) / scale,
            (p.y - wrist.y) / scale,
            (p.z - wrist.z) / scale
        ])

    return vector


def feature_distance(a, b):
    if not a or not b or len(a) != len(b):
        return 999.0

    total = 0.0

    for x, y in zip(a, b):
        total += abs(x - y)

    return total / len(a)


def average_vectors(vectors):
    if not vectors:
        return None

    size = len(vectors[0])
    result = [0.0] * size

    for vector in vectors:
        for i, value in enumerate(vector):
            result[i] += value

    count = float(len(vectors))

    return [value / count for value in result]


def next_gesture_name():
    number = 1

    while f"gesture_{number}" in custom_gestures:
        number += 1

    return f"gesture_{number}"


def trigger_custom_action(action):
    try:
        if action == "SCREENSHOT":
            import pyautogui
            image = pyautogui.screenshot()
            stamp = time.strftime("%Y%m%d_%H%M%S")
            path = os.path.join(
                os.path.expanduser("~/Pictures"),
                f"SAI_Gesture_{stamp}.png"
            )
            os.makedirs(os.path.dirname(path), exist_ok=True)
            image.save(path)
            return True

        if action == "PLAY_PAUSE":
            pyautogui.press("playpause")
            return True

        if action == "NEXT_TRACK":
            pyautogui.press("nexttrack")
            return True

        if action == "PREVIOUS_TRACK":
            pyautogui.press("prevtrack")
            return True

        if action == "SHOW_DESKTOP":
            pyautogui.hotkey("win", "d")
            return True

        if action == "CALCULATOR":
            os.system("start calc")
            return True

        if action == "OPEN_BROWSER":
            webbrowser.open("https://www.google.com")
            return True

    except Exception as exc:
        print("Custom gesture action error:", exc)

    return False


def draw_circle_marker(frame, x, y, radius, label, color):
    cv2.circle(frame, (int(x), int(y)), radius, color, 2)
    cv2.putText(
        frame,
        label,
        (int(x) + radius + 6, int(y) + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        color,
        1,
        cv2.LINE_AA
    )


def draw_app_arrow(frame, direction, w, h, progress=0.0):
    cx = w // 2
    cy = 62
    length = 75
    color = (0, 255, 255)

    if direction > 0:
        p1 = (cx - length, cy)
        p2 = (cx + length, cy)
        cv2.arrowedLine(frame, p1, p2, color, 4, tipLength=0.22)
        text = "NEXT APP  →"
    else:
        p1 = (cx + length, cy)
        p2 = (cx - length, cy)
        cv2.arrowedLine(frame, p1, p2, color, 4, tipLength=0.22)
        text = "←  PREVIOUS APP"

    cv2.putText(
        frame,
        text,
        (cx - 72, cy + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        color,
        2,
        cv2.LINE_AA
    )

    progress = clamp(progress, 0.0, 1.0)
    bar_w = 180
    x1 = cx - bar_w // 2
    x2 = x1 + int(bar_w * progress)
    cv2.rectangle(frame, (x1, cy + 42), (x1 + bar_w, cy + 50), (80, 80, 80), 1)
    if x2 > x1:
        cv2.rectangle(frame, (x1, cy + 42), (x2, cy + 50), color, -1)


def add_app_sample(x, y, current_time):



    app_history.append(

        (

            x,

            y,

            current_time

        )

    )



    if len(app_history) > APP_HISTORY_SIZE:



        app_history.pop(0)





# ============================================================

# MAIN LOOP

# ============================================================



try:



    while True:



        # ====================================================

        # READ CAMERA

        # ====================================================



        success, frame = cap.read()





        if not success:



            print("ERROR: Could not read camera.")



            break





        # ====================================================

        # MIRROR CAMERA

        # ====================================================



        frame = cv2.flip(

            frame,

            1

        )





        h, w, _ = frame.shape





        # ====================================================

        # CONTROL AREA

        # ====================================================



        cv2.rectangle(

            frame,



            (

                FRAME_REDUCTION,

                FRAME_REDUCTION

            ),



            (

                w - FRAME_REDUCTION,

                h - FRAME_REDUCTION

            ),



            (255, 0, 255),



            2

        )





        # ====================================================

        # MEDIAPIPE

        # ====================================================



        rgb = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2RGB

        )





        rgb.flags.writeable = False





        results = hands.process(

            rgb

        )





        rgb.flags.writeable = True





        # ====================================================

        # HAND DETECTED

        # ====================================================



        if results.multi_hand_landmarks:



            hand = results.multi_hand_landmarks[0]





            # =================================================

            # DRAW HAND

            # =================================================



            mp_draw.draw_landmarks(

                frame,

                hand,

                mp_hands.HAND_CONNECTIONS

            )





            lm = hand.landmark
            # LANDMARKS

            # =================================================



            wrist = lm[0]



            thumb = lm[4]



            index = lm[8]



            middle = lm[12]



            ring = lm[16]



            pinky = lm[20]





            index_pip = lm[6]



            middle_pip = lm[10]



            ring_pip = lm[14]



            pinky_pip = lm[18]





            index_mcp = lm[5]



            middle_mcp = lm[9]



            ring_mcp = lm[13]



            pinky_mcp = lm[17]





            # =================================================

            # PIXEL COORDINATES

            # =================================================



            wrist_x = int(wrist.x * w)

            wrist_y = int(wrist.y * h)



            thumb_x = int(thumb.x * w)

            thumb_y = int(thumb.y * h)



            index_x = int(index.x * w)

            index_y = int(index.y * h)



            middle_x = int(middle.x * w)

            middle_y = int(middle.y * h)



            ring_x = int(ring.x * w)

            ring_y = int(ring.y * h)



            pinky_x = int(pinky.x * w)

            pinky_y = int(pinky.y * h)





            index_pip_x = int(index_pip.x * w)

            index_pip_y = int(index_pip.y * h)



            middle_pip_x = int(middle_pip.x * w)

            middle_pip_y = int(middle_pip.y * h)



            ring_pip_x = int(ring_pip.x * w)

            ring_pip_y = int(ring_pip.y * h)



            pinky_pip_x = int(pinky_pip.x * w)

            pinky_pip_y = int(pinky_pip.y * h)





            index_mcp_x = int(index_mcp.x * w)

            index_mcp_y = int(index_mcp.y * h)



            middle_mcp_x = int(middle_mcp.x * w)

            middle_mcp_y = int(middle_mcp.y * h)



            ring_mcp_x = int(ring_mcp.x * w)

            ring_mcp_y = int(ring_mcp.y * h)



            pinky_mcp_x = int(pinky_mcp.x * w)

            pinky_mcp_y = int(pinky_mcp.y * h)





            # =================================================

            # PALM WIDTH

            # =================================================



            palm_width = distance(

                index_mcp_x,

                index_mcp_y,

                pinky_mcp_x,

                pinky_mcp_y

            )





            if palm_width < 1:



                palm_width = 1





            # =================================================

            # INDEX + MIDDLE DISTANCE

            # =================================================



            index_middle_distance = distance(

                index_x,

                index_y,

                middle_x,

                middle_y

            )





            index_middle_ratio = (

                index_middle_distance

                /

                palm_width

            )





            # =================================================

            # THUMB + MIDDLE

            # =================================================



            middle_thumb_distance = distance(

                middle_x,

                middle_y,

                thumb_x,

                thumb_y

            )





            middle_thumb_ratio = (

                middle_thumb_distance

                /

                palm_width

            )





            # =================================================

            # CLICK

            # =================================================



            index_middle_close = (

                index_middle_ratio

                <

                CLICK_START

            )





            index_middle_released = (

                index_middle_ratio

                >

                CLICK_RELEASE

            )





            # =================================================

            # RIGHT CLICK

            # =================================================



            right_is_pinched = (

                middle_thumb_ratio

                <

                RIGHT_CLICK_THRESHOLD

            )





            

            right_is_pinched = (

                middle_thumb_ratio
                <
                RIGHT_CLICK_THRESHOLD
            )


            # =================================================
            # CUSTOM GESTURE LEARNING / MATCHING
            # =================================================

            current_time = time.perf_counter()
            current_custom_features = gesture_feature_vector(lm)

            if learning_active and learning_phase == "capture":
                learning_samples.append(current_custom_features)

                if len(learning_samples) >= learning_target_frames:
                    learning_template = average_vectors(
                        learning_samples
                    )
                    learning_name = next_gesture_name()
                    learning_phase = "choose_action"

            elif (
                not learning_active
                and custom_gestures
                and not index_middle_close
                and not right_is_pinched
            ):
                best_name = None
                best_distance = 999.0

                for name, data in custom_gestures.items():
                    template = data.get("template")

                    if not template:
                        continue

                    d = feature_distance(
                        current_custom_features,
                        template
                    )

                    if d < best_distance:
                        best_distance = d
                        best_name = name

                if (
                    best_name is not None
                    and best_distance <= CUSTOM_MATCH_THRESHOLD
                ):
                    custom_match_count += 1
                    custom_release_count = 0
                    last_custom_name = best_name

                    if (
                        custom_match_count >= CUSTOM_CONFIRM_FRAMES
                        and not custom_trigger_locked
                        and (
                            current_time - last_custom_trigger_time
                            >= CUSTOM_TRIGGER_COOLDOWN
                        )
                    ):
                        action = custom_gestures[
                            best_name
                        ].get("action", "")

                        if trigger_custom_action(action):
                            gesture = f"CUSTOM: {action}"
                            last_custom_trigger_time = current_time
                            custom_trigger_locked = True

                else:
                    custom_match_count = 0
                    custom_release_count += 1

                    if custom_release_count >= CUSTOM_RELEASE_FRAMES:
                        custom_trigger_locked = False
                        last_custom_name = ""


# =================================================

            # FINGER EXTENSION

            # =================================================

            #

            # PIP comparison makes index recognition stronger.

            # =================================================



            index_extended = (

                index_y

                <

                index_pip_y - 5

            )





            middle_extended = (

                middle_y

                <

                middle_pip_y - 5

            )





            ring_extended = (

                ring_y

                <

                ring_pip_y - 5

            )





            pinky_extended = (

                pinky_y

                <

                pinky_pip_y - 5

            )





            # =================================================

            # OPEN HAND

            # =================================================



            open_finger_count = sum(

                [

                    index_extended,

                    middle_extended,

                    ring_extended,

                    pinky_extended

                ]

            )





            open_hand = (

                open_finger_count == 4

            )





            # =================================================

            # INDEX-ONLY MOUSE MODE

            # =================================================



            index_mouse_mode = (



                index_extended



                and



                not middle_extended



                and



                not ring_extended



                and



                not pinky_extended



                and



                not index_middle_close



                and



                not right_is_pinched



            )





            # =================================================

            # PALM CENTER

            # =================================================



            palm_center_x = int(

                (

                    wrist_x

                    +

                    index_mcp_x

                    +

                    middle_mcp_x

                    +

                    ring_mcp_x

                    +

                    pinky_mcp_x

                ) / 5

            )





            palm_center_y = int(

                (

                    wrist_y

                    +

                    index_mcp_y

                    +

                    middle_mcp_y

                    +

                    ring_mcp_y

                    +

                    pinky_mcp_y

                ) / 5

            )





            current_time = time.perf_counter()





            # =================================================

            # APP SWITCHING

            # =================================================



            if (

                not learning_active

                and

                open_hand



                and



                not index_middle_close



                and



                not right_is_pinched



                and



                not dragging



            ):



                add_app_sample(

                    palm_center_x,

                    palm_center_y,

                    current_time

                )





                if not app_gesture_active:



                    app_gesture_active = True



                    app_gesture_start_time = (

                        current_time

                    )



                    app_start_x = (

                        palm_center_x

                    )



                    app_start_y = (

                        palm_center_y

                    )





                else:



                    total_dx = (

                        palm_center_x

                        -

                        app_start_x

                    )





                    total_dy = (

                        palm_center_y

                        -

                        app_start_y

                    )





                    gesture_time = (

                        current_time

                        -

                        app_gesture_start_time

                    )





                    horizontal_distance = abs(

                        total_dx

                    )





                    vertical_distance = abs(

                        total_dy

                    )





                    velocity = 0





                    if len(app_history) >= 2:



                        first_x = app_history[0][0]

                        first_y = app_history[0][1]

                        first_time = app_history[0][2]



                        last_x = app_history[-1][0]

                        last_y = app_history[-1][1]

                        last_time = app_history[-1][2]





                        history_distance = math.hypot(

                            last_x - first_x,

                            last_y - first_y

                        )





                        history_time = (

                            last_time

                            -

                            first_time

                        )





                        if history_time > 0:



                            velocity = (

                                history_distance

                                /

                                history_time

                            )





                    horizontal_dominant = (

                        horizontal_distance

                        >

                        vertical_distance

                        *

                        APP_HORIZONTAL_RATIO

                    )





                    if (



                        horizontal_distance

                        >=

                        APP_MIN_DISTANCE



                        and



                        velocity

                        >=

                        APP_MIN_SPEED



                        and



                        horizontal_dominant



                        and



                        gesture_time

                        <=

                        APP_MAX_GESTURE_TIME



                        and



                        not app_switch_locked



                        and



                        (

                            current_time

                            -

                            last_app_switch_time

                        )

                        >

                        APP_SWITCH_COOLDOWN



                    ):



                        if total_dx > 0:



                            pyautogui.hotkey(

                                "alt",

                                "tab"

                            )



                            gesture = "NEXT APP"



                        else:



                            pyautogui.hotkey(

                                "alt",

                                "shift",

                                "tab"

                            )



                            gesture = "PREVIOUS APP"





                        app_switch_locked = True



                        last_app_switch_time = (

                            current_time

                        )



                        app_start_x = (

                            palm_center_x

                        )



                        app_start_y = (

                            palm_center_y

                        )



                        app_gesture_start_time = (

                            current_time

                        )



                        clear_app_history()





            else:



                app_gesture_active = False



                app_gesture_start_time = None



                app_start_x = None



                app_start_y = None



                clear_app_history()





                if not open_hand:



                    app_switch_locked = False





            # =================================================

            # CONTROL AREA

            # =================================================



            inside_area = (



                FRAME_REDUCTION

                <

                index_x

                <

                w - FRAME_REDUCTION



                and



                FRAME_REDUCTION

                <

                index_y

                <

                h - FRAME_REDUCTION



            )





            # =================================================

            # CURSOR LOCK

            # =================================================



            if cursor_locked:



                pyautogui.moveTo(

                    int(locked_mouse_x),

                    int(locked_mouse_y),

                    duration=0

                )





            # =================================================

            # INDEX FINGER MOUSE

            # =================================================

            #

            # ☝️ ONLY INDEX FINGER CONTROLS MOUSE.

            # =================================================



            elif (

                not learning_active

                and

                index_mouse_mode



                and



                inside_area



            ):



                target_x = (



                    (

                        index_x

                        -

                        FRAME_REDUCTION

                    )



                    /



                    (

                        w

                        -

                        2 * FRAME_REDUCTION

                    )



                    *



                    screen_width

                )





                target_y = (



                    (

                        index_y

                        -

                        FRAME_REDUCTION

                    )



                    /



                    (

                        h

                        -

                        2 * FRAME_REDUCTION

                    )



                    *



                    screen_height

                )





                target_x = clamp(

                    target_x,

                    0,

                    screen_width - 1

                )





                target_y = clamp(

                    target_y,

                    0,

                    screen_height - 1

                )





                dx = (

                    target_x

                    -

                    previous_mouse_x

                )





                dy = (

                    target_y

                    -

                    previous_mouse_y

                )





                movement = math.hypot(

                    dx,

                    dy

                )





                if movement > DEADZONE:



                    if movement < 30:



                        alpha = SMOOTH_ALPHA_SMALL



                    elif movement < 100:



                        alpha = SMOOTH_ALPHA_MEDIUM



                    else:



                        alpha = SMOOTH_ALPHA_FAST





                    current_x = (

                        previous_mouse_x

                        +

                        dx * alpha

                    )





                    current_y = (

                        previous_mouse_y

                        +

                        dy * alpha

                    )





                    pyautogui.moveTo(

                        int(current_x),

                        int(current_y),

                        duration=0

                    )





                    previous_mouse_x = current_x

                    previous_mouse_y = current_y





                    gesture = "MOUSE"





            # =================================================

            # LEFT CLICK / DRAG

            # =================================================



            if index_middle_close and not learning_active:



                if not left_gesture:



                    click_confirm_counter += 1





                    if (

                        click_confirm_counter

                        >=

                        CLICK_CONFIRM_FRAMES

                    ):



                        left_gesture = True





                        mouse_x, mouse_y = (

                            pyautogui.position()

                        )





                        locked_mouse_x = mouse_x

                        locked_mouse_y = mouse_y





                        previous_mouse_x = mouse_x

                        previous_mouse_y = mouse_y





                        cursor_locked = True





                        gesture_started_at = (

                            time.perf_counter()

                        )





                        gesture = "CLICK READY"





                else:



                    click_confirm_counter = (

                        CLICK_CONFIRM_FRAMES

                    )





                    if cursor_locked:



                        pyautogui.moveTo(

                            int(locked_mouse_x),

                            int(locked_mouse_y),

                            duration=0

                        )





                    if (

                        gesture_started_at

                        is not None

                    ):



                        hold_time = (

                            time.perf_counter()

                            -

                            gesture_started_at

                        )





                        if (



                            hold_time

                            >=

                            DRAG_HOLD_TIME



                            and



                            not dragging



                        ):



                            pyautogui.mouseDown()



                            dragging = True



                            cursor_locked = False



                            gesture = "DRAGGING"





            # =================================================

            # CLICK RELEASE

            # =================================================



            elif index_middle_released:



                click_confirm_counter = 0





                if left_gesture:



                    release_time = (

                        time.perf_counter()

                    )





                    hold_time = 0





                    if (

                        gesture_started_at

                        is not None

                    ):



                        hold_time = (

                            release_time

                            -

                            gesture_started_at

                        )





                    # -----------------------------------------

                    # DRAG RELEASE

                    # -----------------------------------------



                    if dragging:



                        pyautogui.mouseUp()



                        dragging = False



                        gesture = "DROP"





                    # -----------------------------------------

                    # NORMAL CLICK

                    # -----------------------------------------



                    elif (

                        hold_time

                        <

                        DRAG_HOLD_TIME

                    ):



                        if (

                            release_time

                            -

                            last_click_time

                            >

                            CLICK_COOLDOWN

                        ):



                            if (

                                release_time

                                -

                                last_left_click_time

                                <=

                                DOUBLE_CLICK_WINDOW

                            ):



                                pyautogui.doubleClick(

                                    interval=0.08

                                )



                                gesture = (

                                    "DOUBLE CLICK"

                                )



                                last_left_click_time = 0



                            else:



                                pyautogui.click()



                                gesture = (

                                    "LEFT CLICK"

                                )



                                last_left_click_time = (

                                    release_time

                                )





                            last_click_time = (

                                release_time

                            )





                    # -----------------------------------------

                    # UNLOCK AFTER CLICK

                    # -----------------------------------------



                    left_gesture = False



                    gesture_started_at = None



                    cursor_locked = False



                    locked_mouse_x = None

                    locked_mouse_y = None





            # =================================================

            # RIGHT CLICK

            # =================================================



            if (

                not learning_active

                and

                right_is_pinched



                and



                not index_middle_close



            ):



                if not right_gesture:



                    current_time = (

                        time.perf_counter()

                    )





                    if (

                        current_time

                        -

                        last_click_time

                        >

                        CLICK_COOLDOWN

                    ):



                        pyautogui.rightClick()



                        last_click_time = (

                            current_time

                        )



                        gesture = "RIGHT CLICK"





                    right_gesture = True





            elif not right_is_pinched:



                right_gesture = False





            # =================================================

            # TWO-FINGER SCROLL

            # =================================================



            two_fingers = (



                index_extended



                and



                middle_extended



                and



                not ring_extended



                and



                not pinky_extended



            )





            if (

                not learning_active

                and

                two_fingers



                and



                not index_middle_close



                and



                not right_is_pinched



                and



                not open_hand



            ):



                average_x = (

                    index_x

                    +

                    middle_x

                ) / 2





                average_y = (

                    index_y

                    +

                    middle_y

                ) / 2





                # ---------------------------------------------

                # VERTICAL SCROLL

                # ---------------------------------------------



                if (

                    previous_scroll_y

                    is not None

                ):



                    scroll_delta = (

                        previous_scroll_y

                        -

                        average_y

                    )





                    if (

                        abs(scroll_delta)

                        >

                        SCROLL_DEADZONE

                    ):



                        scroll_amount = (

                            scroll_delta

                            *

                            SCROLL_MULTIPLIER

                        )





                        scroll_amount = clamp(

                            scroll_amount,

                            -5,

                            5

                        )





                        if (

                            abs(scroll_amount)

                            >=

                            1

                        ):



                            pyautogui.scroll(

                                int(scroll_amount)

                            )



                            gesture = "SCROLL"





                # ---------------------------------------------

                # HORIZONTAL SCROLL

                # ---------------------------------------------



                if (

                    previous_scroll_x

                    is not None

                ):



                    horizontal_delta = (

                        previous_scroll_x

                        -

                        average_x

                    )





                    if (

                        abs(horizontal_delta)

                        >

                        SCROLL_DEADZONE

                    ):



                        horizontal_amount = (

                            horizontal_delta

                            *

                            SCROLL_MULTIPLIER

                        )





                        horizontal_amount = clamp(

                            horizontal_amount,

                            -5,

                            5

                        )





                        if (

                            hasattr(

                                pyautogui,

                                "hscroll"

                            )

                            and

                            abs(horizontal_amount)

                            >=

                            1

                        ):



                            pyautogui.hscroll(

                                int(horizontal_amount)

                            )



                            gesture = (

                                "HORIZONTAL SCROLL"

                            )





                previous_scroll_x = average_x

                previous_scroll_y = average_y





            else:



                previous_scroll_x = None

                previous_scroll_y = None





            # =================================================

            # VISUAL MARKERS

            # =================================================



            cv2.circle(

                frame,

                (index_x, index_y),

                8,

                (0, 255, 0),

                cv2.FILLED

            )





            cv2.circle(

                frame,

                (middle_x, middle_y),

                8,

                (0, 0, 255),

                cv2.FILLED

            )





            cv2.circle(

                frame,

                (thumb_x, thumb_y),

                8,

                (255, 0, 0),

                cv2.FILLED

            )





            cv2.line(

                frame,



                (index_x, index_y),



                (middle_x, middle_y),



                (0, 255, 255),



                2

            )





            # =================================================

            # STATUS

            # =================================================



            cv2.putText(

                frame,

                "HAND DETECTED",

                (10, 28),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.60,

                (0, 255, 0),

                2

            )





            cv2.putText(

                frame,

                f"Gesture: {gesture}",

                (10, 55),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (0, 255, 255),

                2

            )





            cv2.putText(

                frame,

                f"Index-Middle: {index_middle_ratio:.2f}",

                (10, 82),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.50,

                (255, 255, 255),

                1

            )





            cv2.putText(

                frame,

                f"INDEX MOUSE: {'ON' if index_mouse_mode else 'OFF'}",

                (10, 105),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.50,

                (0, 255, 0) if index_mouse_mode

                else (255, 255, 255),

                2

            )





            cv2.putText(

                frame,

                f"Fingers: {open_finger_count}/4",

                (10, 128),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.50,

                (255, 255, 255),

                1

            )





            if cursor_locked:



                cv2.putText(

                    frame,

                    "CLICK LOCKED",

                    (10, 153),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.50,

                    (0, 165, 255),

                    2

                )





            if open_hand:



                cv2.putText(

                    frame,

                    "OPEN PALM - MOUSE STOP",

                    (10, 178),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.50,

                    (0, 165, 255),

                    2

                )





            cv2.putText(

                frame,

                "INDEX = MOUSE",

                (10, h - 55),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.45,

                (255, 255, 255),

                1

            )





            cv2.putText(

                frame,

                "INDEX + MIDDLE = CLICK",

                (10, h - 34),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.45,

                (255, 255, 255),

                1

            )





            cv2.putText(

                frame,

                "OPEN PALM WAVE = APP SWITCH | Q = EXIT",

                (10, h - 12),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.40,

                (255, 255, 255),

                1

            )





        # ====================================================

        # NO HAND

        # ====================================================



        else:



            if dragging:



                pyautogui.mouseUp()



                dragging = False





            left_gesture = False



            right_gesture = False



            click_confirm_counter = 0



            gesture_started_at = None





            cursor_locked = False



            locked_mouse_x = None

            locked_mouse_y = None





            previous_scroll_x = None

            previous_scroll_y = None





            app_gesture_active = False



            app_gesture_start_time = None



            app_start_x = None

            app_start_y = None



            app_switch_locked = False



            clear_app_history()





            gesture = "NO HAND"





            cv2.putText(

                frame,

                "NO HAND DETECTED",

                (10, 28),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.60,

                (0, 0, 255),

                2

            )





        # ====================================================

        # FPS

        # ====================================================



        current_time = time.perf_counter()



        elapsed = (

            current_time

            -

            previous_time

        )





        if elapsed > 0:



            instant_fps = 1.0 / elapsed



            fps = (

                fps * 0.90

                +

                instant_fps * 0.10

            )





        previous_time = current_time





        cv2.putText(

            frame,

            f"FPS: {int(fps)}",

            (

                w - 120,

                28

            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.60,

            (0, 255, 255),

            2

        )





        # ====================================================

        # SHOW

        # ====================================================



        cv2.imshow(

            "SAI Air Mouse",

            frame

        )





        # ====================================================

        # EXIT

        # ====================================================



        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        # L = learn a new custom hand gesture.
        if key == ord("l") and not learning_active:
            learning_active = True
            learning_phase = "capture"
            learning_samples = []
            learning_target_frames = CUSTOM_CAPTURE_FRAMES
            learning_name = None
            learning_template = None
            learning_action = None
            custom_match_count = 0
            custom_release_count = 0
            custom_trigger_locked = False
            gesture = "LEARNING"

        # After capture, press 1-7 to assign an action.
        if (
            learning_active
            and learning_phase == "choose_action"
            and chr(key) in CUSTOM_ACTIONS
        ):
            learning_action = CUSTOM_ACTIONS[chr(key)]

            custom_gestures[learning_name] = {
                "action": learning_action,
                "template": learning_template,
                "created": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            save_custom_gestures()

            learning_active = False
            learning_phase = "idle"
            learning_samples = []
            learning_template = None
            gesture = f"SAVED: {learning_action}"






# ============================================================

# CLEANUP

# ============================================================



finally:



    if dragging:



        pyautogui.mouseUp()





    cap.release()



    cv2.destroyAllWindows()



    hands.close()
