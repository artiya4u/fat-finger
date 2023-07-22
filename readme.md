# Fat Finger

A Tinder bot based on user profile investment.
More info on [my blog post](https://medium.com/@artiya4u/fatfinger-a-pretty-good-tinder-bot-f76c468168d8)

## How to use

- Open Chrome and go to [Extension Settings](chrome://extensions/) and enable developer mode and click on the "Load
  unpacked extension" button and select the `chrome_extension` folder.
- Login with your Tinder account on [https://tinder.com](https://tinder.com)
- Go to [https://tinder.com/app/recs](https://tinder.com/app/recs)

## Run server locally

- Install requirements `pip install -r requirements.txt`
- Download models from [here](https://drive.google.com/drive/folders/1t6qJ6ThV2UPhXmc_lg3qXK1f0me4TPN_?usp=sharing)
  and put it in the `models` folder.
- Set Python path `export PYTHONPATH=$PYTHONPATH:./app`
- Run the api using command `python3 -m uvicorn api:app --host 0.0.0.0 --port 8008`
- change the `chrome_extension/content.js` constant `BASE_API_URL` with your local api url http://127.0.0.1:8008.
  to use the local server.