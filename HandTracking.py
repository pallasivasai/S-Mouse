import cv2
import mediapipe as mp
import math
import time


class HandDetector:
    def __init__(
        self,
        mode=False,
        max_hands=2,
        detection_confidence=0.5,
        tracking_confidence=0.5,
    ):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
            model_complexity=0,
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None
        self.lm_list = []

    def find_hands(self, img, draw=True):
        if img is None:
            return None

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        self.results = self.hands.process(rgb)
        rgb.flags.writeable = True

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                    )

        return img

    def find_position(self, img, hand_no=0, draw=True):
        x_list = []
        y_list = []
        bbox = []
        self.lm_list = []

        if (
            self.results is None
            or not self.results.multi_hand_landmarks
            or hand_no >= len(self.results.multi_hand_landmarks)
        ):
            return self.lm_list, bbox

        my_hand = self.results.multi_hand_landmarks[hand_no]
        h, w, _ = img.shape

        for landmark_id, landmark in enumerate(my_hand.landmark):
            cx = int(landmark.x * w)
            cy = int(landmark.y * h)

            x_list.append(cx)
            y_list.append(cy)

            self.lm_list.append([landmark_id, cx, cy])

            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if x_list and y_list:
            xmin, xmax = min(x_list), max(x_list)
            ymin, ymax = min(y_list), max(y_list)
            bbox = (xmin, ymin, xmax, ymax)

            if draw:
                cv2.rectangle(
                    img,
                    (xmin - 20, ymin - 20),
                    (xmax + 20, ymax + 20),
                    (0, 255, 0),
                    2,
                )

        return self.lm_list, bbox

    def fingers_up(self):
        fingers = []

        if len(self.lm_list) < 21:
            return fingers

        if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for finger_id in range(1, 5):
            if self.lm_list[self.tip_ids[finger_id]][2] < self.lm_list[self.tip_ids[finger_id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def find_distance(
        self,
        p1,
        p2,
        img,
        draw=True,
        radius=15,
        thickness=3,
    ):
        if len(self.lm_list) < 21:
            return 0, img, []

        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), thickness)
            cv2.circle(img, (x1, y1), radius, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), radius, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), radius, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    previous_time = 0

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    detector = HandDetector(
        max_hands=2,
        detection_confidence=0.5,
        tracking_confidence=0.5,
    )

    try:
        while True:
            success, img = cap.read()

            if not success:
                print("ERROR: Could not read frame.")
                break

            img = cv2.flip(img, 1)
            img = detector.find_hands(img)
            lm_list, _ = detector.find_position(img)

            if lm_list:
                print(lm_list[4])

            current_time = time.time()
            difference = current_time - previous_time
            fps = 1 / difference if difference > 0 else 0
            previous_time = current_time

            cv2.putText(
                img,
                f"FPS: {int(fps)}",
                (10, 50),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (255, 0, 255),
                2,
            )

            cv2.imshow("Hand Detection", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.hands.close()


if __name__ == "__main__":
    main()
