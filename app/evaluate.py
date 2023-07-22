import random
import statistics

from htmnet.inference_fbp import HMTNetRecognizer, crop_face_from_image


class Evaluator:

    def evaluate(self, profile) -> (bool, float):
        """
        Evaluate the profile photos to see if it's a hot.
        """
        pass


class PointBasedEvaluator(Evaluator):

    @staticmethod
    def contains_alien_character(text):
        for char in text:
            code_point = ord(char)
            if 3584 <= code_point <= 3711 or 19968 <= code_point <= 40959:
                return True
        return False

    @staticmethod
    def filter_text(text):
        return text.replace(" ", "").replace(".", "").replace("-", "")

    def evaluate(self, profile) -> (bool, float):
        point = 0

        # photos
        point += len(profile["photos"]) * 0.4

        # instagram
        if profile["instagram"] != "":
            point += 4.6

        if profile["active"]:
            point += 3

        if profile["verified"]:
            point += 3

        # completed profile bio
        if len(profile["bio"]) > 55:
            point += 3
        elif len(profile["bio"]) > 21:
            point += 2

        if self.contains_alien_character(profile["name"]):
            point -= 4

        if self.contains_alien_character(profile["bio"]):
            point -= 2

        if self.contains_alien_character(profile["livesIn"]):
            point -= 2

        if self.contains_alien_character(profile["job"]):
            point -= 3

        if self.contains_alien_character(profile["school"]):
            point -= 3

        # job and school
        if self.filter_text(profile["job"]) != "" and not self.contains_alien_character(profile["job"]):
            point += 2

        if self.filter_text(profile["school"]) != "" and not self.contains_alien_character(profile["school"]):
            point += 1

        # passions and lifestyles
        if len(profile["tags"]) > 0:
            point += len(profile["tags"]) * 0.3

        # dog or cat
        if '🐶' in profile["bio"] or '🐱' in profile["bio"]:
            point += 1

        if '📷' in profile["bio"]:
            point += 1

        # random 0-2
        point += random.random() * 2

        # adjust by age
        if profile["age"] is not None:
            if profile["age"] < 25:
                point *= 1.1

            if profile["age"] >= 30:
                point *= 0.9

            if profile["age"] >= 32:
                point *= 0.85

        hot = point >= 11
        return hot, point


class HMTNetEvaluator(Evaluator):
    def __init__(self):
        self.hmtnet_recognizer = HMTNetRecognizer()

    def evaluate(self, profile) -> (bool, float):
        face_count = 0
        scores = []
        for photo in profile["photos"]:
            try:
                crop_image_path = crop_face_from_image(photo)
                if crop_image_path is None:
                    continue
                face_count += 1
                score = self.hmtnet_recognizer.infer(crop_image_path)
            except Exception as e:
                continue

            if score < 2.5:  # skip low score
                return False, score
            if score > 4.6:  # outlined
                face_count -= 1
                continue

            scores.append(score)

        if face_count < 3:
            return False, face_count

        return True, statistics.mean(scores)
