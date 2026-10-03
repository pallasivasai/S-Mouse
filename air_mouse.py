import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ============================================================
# SAI AIR MOUSE - SMOOTH + RELIABLE CLICK EDITION
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TARGET_FPS = 60

FRAME_REDUCTION = 60

# Cursor
DEADZONE = 1.5
BASE_SMOOTHING = 0.22

# Reliable pinch detection
PINCH_THRESHOLD = 0.52
PINCH_RELEASE = 0.70
PINCH_CONFIRM_FRAMES = 3

# Click / double click
CLICK_COOLDOWN = 0.25
DOUBLE_CLICK_TIME = 0.45
MIN_CLICK_HOLD = 0.06
DRAG_HOLD_TIME = 0.55

# Scroll
SCROLL_DEADZONE = 10
SCROLL_SCALE = 0.12

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.50,
    min_tracking_confidence=0.50,
)

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    raise SystemExit

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

screen_width, screen_height = pyautogui.size()

previous_mouse_x = screen_width / 2
previous_mouse_y = screen_height / 2

# Click state
left_pinch_active = False
pinch_confirmed = False
pinch_frames = 0
pinch_start_time = None

# Right-click state
right_pinch_active = False
right_pinch_frames = 0

# Drag
dragging = False

# Click timing
last_click_time = 0.0
last_pinch_time = 0.0

# Scroll
previous_scroll_x = None
previous_scroll_y = None

gesture_name = "READY"

# FPS
previous_time = time.perf_counter()
fps = 0.0


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


try:
    while True:

        success, img = cap.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break

        # Mirror camera
        img = cv2.flip(img, 1)

        h, w, _ = img.shape

        # Control area
        cv2.rectangle(
            img,
            (FRAME_REDUCTION, FRAME_REDUCTION),
            (w - FRAME_REDUCTION, h - FRAME_REDUCTION),
            (255, 0, 255),
            2,
        )

        # MediaPipe
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        rgb.flags.writeable = True

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            mp_draw.draw_landmarks(
                img,
                hand,
                mp_hands.HAND_CONNECTIONS,
            )

            lm = hand.landmark

            wrist = lm[0]
            thumb = lm[4]
            index = lm[8]
            middle = lm[12]

            wrist_x = int(wrist.x * w)
            wrist_y = int(wrist.y * h)

            thumb_x = int(thumb.x * w)
            thumb_y = int(thumb.y * h)

            index_x = int(index.x * w)
            index_y = int(index.y * h)

            middle_x = int(middle.x * w)
            middle_y = int(middle.y * h)

            # Normalize pinch distance by palm size.
            palm_size = distance(
                wrist_x,
                wrist_y,
                int(lm[5].x * w),
                int(lm[5].y * h),
            )

            palm_size = max(palm_size, 1.0)

            index_thumb_distance = distance(
                index_x,
                index_y,
                thumb_x,
                thumb_y,
            )

            middle_thumb_distance = distance(
                middle_x,
                middle_y,
                thumb_x,
                thumb_y,
            )

            pinch_ratio = (
                index_thumb_distance / palm_size
            )

            right_pinch_ratio = (
                middle_thumb_distance / palm_size
            )

            # =================================================
            # CURSOR MOVEMENT
            # =================================================

            inside_area = (
                FRAME_REDUCTION < index_x < w - FRAME_REDUCTION
                and
                FRAME_REDUCTION < index_y < h - FRAME_REDUCTION
            )

            right_pinch = (
                right_pinch_ratio < PINCH_THRESHOLD
            )

            if inside_area and not right_pinch:

                target_x = (
                    (index_x - FRAME_REDUCTION)
                    /
                    (w - 2 * FRAME_REDUCTION)
                    *
                    screen_width
                )

                target_y = (
                    (index_y - FRAME_REDUCTION)
                    /
                    (h - 2 * FRAME_REDUCTION)
                    *
                    screen_height
                )

                target_x = clamp(
                    target_x,
                    0,
                    screen_width - 1,
                )

                target_y = clamp(
                    target_y,
                    0,
                    screen_height - 1,
                )

                dx = target_x - previous_mouse_x
                dy = target_y - previous_mouse_y

                movement = math.hypot(dx, dy)

                if movement > DEADZONE:

                    if movement < 35:
                        alpha = 0.15
                    elif movement < 100:
                        alpha = BASE_SMOOTHING
                    else:
                        alpha = 0.55

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
                        duration=0,
                    )

                    previous_mouse_x = current_x
                    previous_mouse_y = current_y

            # =================================================
            # LEFT PINCH - STABLE DETECTION
            # =================================================

            left_pinch = (
                pinch_ratio <= PINCH_THRESHOLD
            )

            released = (
                pinch_ratio >= PINCH_RELEASE
            )

            if left_pinch:

                pinch_frames += 1

                # Only start a gesture after several
                # consecutive frames confirm the pinch.
                if (
                    pinch_frames >= PINCH_CONFIRM_FRAMES
                    and
                    not left_pinch_active
                ):

                    left_pinch_active = True
                    pinch_confirmed = True
                    pinch_start_time = time.perf_counter()

                    gesture_name = "PINCH"

            else:

                pinch_frames = 0

            # =================================================
            # DRAG START
            # =================================================

            if left_pinch_active:

                hold_time = (
                    time.perf_counter()
                    -
                    pinch_start_time
                )

                if (
                    pinch_confirmed
                    and
                    hold_time >= DRAG_HOLD_TIME
                    and
                    not dragging
                ):

                    pyautogui.mouseDown()

                    dragging = True

                    gesture_name = "DRAG"

            # =================================================
            # PINCH RELEASE = CLICK
            # =================================================

            if (
                left_pinch_active
                and
                released
            ):

                release_time = time.perf_counter()

                hold_time = (
                    release_time
                    -
                    pinch_start_time
                )

                # Release a drag.
                if dragging:

                    pyautogui.mouseUp()

                    dragging = False

                    gesture_name = "DROP"

                # Short pinch = click.
                elif (
                    pinch_confirmed
                    and
                    hold_time >= MIN_CLICK_HOLD
                    and
                    release_time - last_click_time
                    >= CLICK_COOLDOWN
                ):

                    # Important:
                    # We perform the second click separately
                    # instead of calling doubleClick(), so the
                    # first click + second quick click becomes a
                    # normal OS double-click sequence.
                    if (
                        release_time - last_pinch_time
                        <= DOUBLE_CLICK_TIME
                    ):

                        pyautogui.click()

                        gesture_name = "DOUBLE CLICK"

                    else:

                        pyautogui.click()

                        gesture_name = "LEFT CLICK"

                    last_click_time = release_time
                    last_pinch_time = release_time

                # Reset the pinch state.
                left_pinch_active = False
                pinch_confirmed = False
                pinch_frames = 0
                pinch_start_time = None

            # =================================================
            # RIGHT CLICK - ALSO STABLE
            # =================================================

            right_pinch_detected = (
                right_pinch_ratio <= PINCH_THRESHOLD
            )

            right_released = (
                right_pinch_ratio >= PINCH_RELEASE
            )

            if right_pinch_detected:

                right_pinch_frames += 1

                if (
                    right_pinch_frames
                    >= PINCH_CONFIRM_FRAMES
                    and
                    not right_pinch_active
                ):

                    current_time = time.perf_counter()

                    if (
                        current_time - last_click_time
                        >= CLICK_COOLDOWN
                    ):

                        pyautogui.rightClick()

                        last_click_time = current_time

                        gesture_name = "RIGHT CLICK"

                    right_pinch_active = True

            else:

                right_pinch_frames = 0

            if right_released:

                right_pinch_active = False
                right_pinch_frames = 0

            # =================================================
            # TWO-FINGER SCROLL
            # =================================================

            index_up = index_y < wrist_y
            middle_up = middle_y < wrist_y

            two_fingers = (
                index_up
                and
                middle_up
            )

            if two_fingers and not left_pinch:

                current_scroll_x = (
                    index_x + middle_x
                ) / 2

                current_scroll_y = (
                    index_y + middle_y
                ) / 2

                if previous_scroll_y is not None:

                    dy_scroll = (
                        previous_scroll_y
                        -
                        current_scroll_y
                    )

                    if abs(dy_scroll) > SCROLL_DEADZONE:

                        amount = clamp(
                            dy_scroll * SCROLL_SCALE,
                            -5,
                            5,
                        )

                        if amount:

                            pyautogui.scroll(
                                int(amount)
                            )

                            gesture_name = "SCROLL"

                if previous_scroll_x is not None:

                    dx_scroll = (
                        previous_scroll_x
                        -
                        current_scroll_x
                    )

                    if abs(dx_scroll) > SCROLL_DEADZONE:

                        amount = clamp(
                            dx_scroll * SCROLL_SCALE,
                            -5,
                            5,
                        )

                        if (
                            amount
                            and
                            hasattr(
                                pyautogui,
                                "hscroll",
                            )
                        ):

                            pyautogui.hscroll(
                                int(amount)
                            )

                            gesture_name = (
                                "HORIZONTAL SCROLL"
                            )

                previous_scroll_x = current_scroll_x
                previous_scroll_y = current_scroll_y

            else:

                previous_scroll_x = None
                previous_scroll_y = None

            # =================================================
            # VISUAL DEBUG
            # =================================================

            cv2.circle(
                img,
                (index_x, index_y),
                7,
                (0, 255, 0),
                cv2.FILLED,
            )

            cv2.circle(
                img,
                (thumb_x, thumb_y),
                7,
                (255, 0, 0),
                cv2.FILLED,
            )

            cv2.line(
                img,
                (index_x, index_y),
                (thumb_x, thumb_y),
                (0, 255, 255),
                2,
            )

            cv2.putText(
                img,
                "HAND DETECTED",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                img,
                gesture_name,
                (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
            )

            cv2.putText(
                img,
                f"Pinch: {pinch_ratio:.2f}",
                (10, 88),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            if dragging:

                cv2.putText(
                    img,
                    "DRAGGING",
                    (10, 118),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 0, 255),
                    2,
                )

        # =====================================================
        # NO HAND
        # =====================================================

        else:

            if dragging:

                pyautogui.mouseUp()

                dragging = False

            left_pinch_active = False
            pinch_confirmed = False
            pinch_frames = 0
            pinch_start_time = None

            right_pinch_active = False
            right_pinch_frames = 0

            previous_scroll_x = None
            previous_scroll_y = None

            gesture_name = "NO HAND"

            cv2.putText(
                img,
                "NO HAND DETECTED",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        # =====================================================
        # FPS
        # =====================================================

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
            img,
            f"FPS: {int(fps)}",
            (w - 125, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

        cv2.imshow(
            "SAI Air Mouse - Advanced",
            img,
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:

    if dragging:
        pyautogui.mouseUp()

    cap.release()
    cv2.destroyAllWindows()
    hands.close()
