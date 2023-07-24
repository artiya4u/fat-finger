import configs

skip_list = configs.settings['skip_list']


def should_skip(text: str) -> bool:
    for word in skip_list:
        if word.upper() in text.upper():
            return True
    return False
