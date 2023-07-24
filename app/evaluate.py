import statistics

from htmnet.inference_fbp import HMTNetRecognizer, crop_face_from_image

from configs import settings


class Evaluator:

    def evaluate(self, profile) -> (bool, float):
        """
        Evaluate the profile photos to see if it's a hot.
        """
        pass


class InvestmentEvaluator(Evaluator):

    def __init__(self):
        self.config = settings['investment_evaluator']

    @staticmethod
    def is_non_english(text):
        for char in text:
            code_point = ord(char)
            # Exclude characters in the ASCII range (English characters)
            if 32 <= code_point <= 127:
                continue
            # Exclude emojis (typically higher Unicode code points)
            if code_point >= 128512:  # Emojis typically start from code point 128512 (U+1F600)
                continue
            return True
        return False

    @staticmethod
    def filter_text(text):
        return text.replace(' ', '').replace('.', '').replace('-', '')

    def evaluate(self, profile) -> (bool, float):
        point = 0

        # photos
        point += len(profile['photos']) * self.config['photos']

        # instagram
        if profile['instagram'] != '':
            point += self.config['instagram']

        if profile['active']:
            point += self.config['active']

        if profile['verified']:
            point += self.config['verified']

        if profile['livesIn'] != '':
            point += self.config['livesIn']

        # completed profile bio
        if len(profile['bio']) > 55:
            point += self.config['bio_long']
        elif len(profile['bio']) > 21:
            point += self.config['bio_short']

        if self.is_non_english(profile['name']):
            point -= self.config['non_english']['name']

        if self.is_non_english(profile['bio']):
            point -= self.config['non_english']['bio']

        if self.is_non_english(profile['livesIn']):
            point -= self.config['non_english']['livesIn']

        if self.is_non_english(profile['job']):
            point -= self.config['non_english']['job']

        if self.is_non_english(profile['school']):
            point -= self.config['non_english']['school']

        # job and school
        if self.filter_text(profile['job']) != '' and not self.is_non_english(profile['job']):
            point += self.config['job']

        if self.filter_text(profile['school']) != '' and not self.is_non_english(profile['school']):
            point += self.config['school']

        # passions and lifestyles
        if len(profile['tags']) > 0:
            point += len(profile['tags']) * self.config['tags']

        # dog or cat
        if '🐶' in profile['bio'] or '🐱' in profile['bio']:
            point += self.config['dog_cat']

        if '📷' in profile['bio']:
            point += self.config['photography']

        # adjust by age for female fertility, not judging.
        if profile['age'] is not None:
            if profile['age'] < 25:
                point *= self.config['age']['<25']

            if profile['age'] >= 30:
                point *= self.config['age']['>=30']

            if profile['age'] >= 35:
                point *= self.config['age']['>=35']

        hot = point >= self.config['hot_threshold']
        return hot, point


class FaceEvaluator(Evaluator):
    def __init__(self):
        self.hmtnet_recognizer = HMTNetRecognizer()
        self.config = settings['face_evaluator']

    def evaluate(self, profile) -> (bool, float):
        face_count = 0
        scores = []
        for photo in profile['photos']:
            try:
                crop_image_path = crop_face_from_image(photo)
                if crop_image_path is None:
                    continue
                score = self.hmtnet_recognizer.infer(crop_image_path)
            except Exception as e:
                continue

            if score < self.config['min_face_score']:  # skip low score
                continue
            if score > self.config['max_face_score']:  # outlined
                continue

            face_count += 1
            scores.append(score)

        # not enough faces
        if face_count < self.config['min_face_count']:
            return False, - (face_count + 10)

        mean_score = statistics.mean(scores)
        return mean_score > self.config['hot_threshold'], mean_score
