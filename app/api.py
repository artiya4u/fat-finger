import asyncio
import json
import os
import shutil
import time
import random
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from evaluate import PointBasedEvaluator, HMTNetEvaluator
from parse_ig import parse_bio
from skip_filter import should_skip

point_based_evaluator = PointBasedEvaluator()
htmnet_evaluator = HMTNetEvaluator()

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists('./photos'):
    os.mkdir('./photos')


def touch(path):
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)


touch('profiles.txt')
touch('swipe.txt')


class Profile(BaseModel):
    name: str
    age: int | None = None
    verified: bool = False
    active: bool = False
    livesIn: str
    bio: str
    job: str
    school: str

    tags: list[str] = []
    photos: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Zwolf Cookie",
                "age": 27,
                "verified": True,
                "livesIn": "Bangkok, Thailand",
                "bio": "I’m a dog person 🐶\nIG : Cookieb2uty\n165cm",
                "job": "Marketing",
                "school": "PSU",
                "tags": ["Dog lover", "Travel", "Netfilx", "Cooking", "Running"],
                "photoUrls": [
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_b16edea3-e424-47be-85d8-a94c2cd210b1.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_6019c045-25bd-4da6-81cb-6577ac2a36ea.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_cb8ef2cd-5db3-4e3c-adf0-7e0308a0e44e.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_6c1ed192-31d3-46ac-a750-786d4056cdcd.jpg",
                    "https://images-ssl.gotinder.com/58789c82d06e40d71ed85d98/640x800_be04a41f-4f7b-45c3-9c88-a1fe1bccda61.jpg"
                ],
            }
        }


class Response(BaseModel):
    code: str
    profile: dict

    class Config:
        json_schema_extra = {
            "example": {
                "code": "ok",
                "profile": {},
            }
        }


def download_image(uid, url):
    """
    Download an image from the url, convert and save it to a jpg.
    """
    try:
        response = requests.get(url, stream=True)
        file_name = f"{time.time_ns()}"
        image_temp = f'./photos/{uid}/{file_name}'
        if url[0:url.find('?')].endswith('.jpg') or url.endswith('.jpg') or url.endswith('.jpeg'):
            image_file_ext = f'{image_temp}.jpg'
        else:
            image_file_ext = f'{image_temp}.webp'

        with open(image_file_ext, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return image_file_ext
    except Exception as e:
        print(e)
        return None


@app.post("/save", response_model=Response)
async def save(profile: Profile):
    """
    Save Tinder profile data.
    """
    uid = f"{time.time_ns()}"  # Use nano time epoch as uid
    user = {
        "uid": uid,
        "active": profile.active,
        "instagram": parse_bio(profile.bio),
        "name": profile.name,
        "age": profile.age,
        "verified": profile.verified,
        "livesIn": profile.livesIn,
        "bio": profile.bio,
        "job": profile.job,
        "school": profile.school,
        "tags": profile.tags,
        "photos": profile.photos,
        "hot": False,
        "score": 0,
        "face_score": 0,
    }

    print('=============================================================================')
    print(f"{user['name']}({user['age']})")
    print(f"instagram={user['instagram']}")
    print(f"active={user['active']}")
    print(f"verified={user['verified']}")
    print(f"tags:{len(user['tags'])}={user['tags']}")
    print(f"photos={len(user['photos'])}")
    print(f"{user['job']} {user['school']} {user['livesIn']}")
    print(f"{user['bio']}")
    print('=============================================================================')

    if should_skip(profile.bio) or should_skip(profile.name) or should_skip(profile.job):
        print("skipped")
        user["hot"] = False
        user["score"] = 0
    else:
        print("evaluating investment score...")
        hot, score = point_based_evaluator.evaluate(user)
        user["score"] = score
        if hot:
            print("evaluating face score...")
            user["photos"] = []
            os.mkdir(f'./photos/{user["uid"]}')
            for photo_url in profile.photos:
                image_file = download_image(user["uid"], photo_url)
                if image_file is not None:
                    user["photos"].append(image_file)
            hot, face_score = htmnet_evaluator.evaluate(user)
            user["hot"] = hot
            user["face_score"] = face_score
        else:
            user["photos"] = profile.photos

    with open('./profiles.txt', 'a') as df:
        df.write(json.dumps(user) + '\n')

    print(f"score={user['score']}")
    print(f"face_score={user['face_score']}")
    print(f"hot={user['hot']}")
    print('=============================================================================')
    return Response(code="ok", profile=user)


class Action(BaseModel):
    profile_id: str
    action_code: int


swiped = {}
swipe_file = open('swipe.txt', 'r')
for line in swipe_file.readlines():
    s = line.strip().split(',')
    if len(s) == 2:
        swiped[s[0]] = s[1]

dataset_file = open('profiles.txt', 'r')
profiles_all = {}
for line in dataset_file.readlines():
    p = json.loads(line)

    # Swipe ig user first.
    if p["instagram"] == "":
        continue

    if len(p["photos"]) == 0:
        continue

    if p["uid"] not in swiped:
        if p["uid"] not in profiles_all:
            profiles_all[p["uid"]] = p


@app.post("/swipe", response_model=Response)
async def swipe(action: Action):
    """
    Swipe a Tinder profile.
    0 = pass
    1 = like
    2 = super-like
    """
    with open('../swipe.txt', 'a') as df:
        if action.profile_id in profiles_all:
            df.write(f'{action.profile_id},{action.action_code}' + '\n')
            swiped[action.profile_id] = str(action.action_code)
            profiles_all.pop(action.profile_id)

    return Response(code="OK", result="SAVED")


@app.get("/profiles")
async def profiles():
    """
    Get 100 date profiles to swipe.
    """

    return random.sample(list(profiles_all.values()), 100)


def loop_error_handler(loop, context: dict):
    print(f'loop error')
    if 'exception' in context:
        print(f"Exception{context['exception']}")


@app.on_event("startup")
async def startup_event():
    print('starting up server')
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(loop_error_handler)


@app.on_event("shutdown")
def shutdown_event():
    print('shutting down server')
    loop = asyncio.get_event_loop()
