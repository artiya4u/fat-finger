import requests
from dynaconf import Dynaconf

envs = Dynaconf(
    envvar_prefix=False,
    environments=True,
    load_dotenv=True,
)


def load_config_from_url(name):
    env_name = f'CONFIG_{name.upper()}_URL'
    config_url = envs.get(env_name, None)
    name = name.lower()
    if config_url is not None:
        path = config_url.rsplit('/', 1)[-1]
        name = f'{name}_{path}'
        print(f'load config [config_{name}.json] from url: {config_url}')
        response = requests.get(config_url)

        # Save the file to disk
        with open(f'./config/config_{name}.json', "wb") as f:
            f.write(response.content)
    else:
        print(f'load config [config_{name}.json] from local file')

    conf = Dynaconf(
        settings_files=[f'./config/config_{name}.json',
                        f'../config/config_{name}.json',
                        f'config_{name}.json',
                        envs.get(env_name, None)],
    )
    return conf


settings = load_config_from_url('settings')
