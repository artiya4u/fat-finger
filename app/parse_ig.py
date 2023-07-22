import json
import re


def parse_ig_line(line: str):
    line = line.strip()
    line = re.sub('[^\x00-\x7F]+', '', line)
    line = line.replace(':', '')
    line = line.replace('-', '')
    line = line.replace('@', '')
    line = line.replace(';', '')
    line = line.strip()
    if len(line) == 0:
        return ''

    line = line.split(' ')[0]

    if line[0] == '.':
        line = line[1:]
        line = line.strip()

    return line


def find_ig_in_text(line: str, tag):
    pos = line.find(tag)
    if pos >= 0:
        pos += len(tag)
    return pos


def parse_bio(bio: str):
    ig = ''
    lines = bio.split('\n')
    for line in lines:
        line = line.strip().lower()
        if line.startswith('instagram'):
            line = line.replace('instagram', '', 1)
            ig = parse_ig_line(line)
            return ig

        if line.startswith('ig'):
            line = line.replace('ig', '', 1)
            ig = parse_ig_line(line)
            return ig

        tags = [
            'ig ', 'ig -', 'ig-', 'ig:', 'ig :', 'ig.', 'ig;', 'ig ;', 'ig@',
            'instagram ', 'instagram -', 'instagram-', 'instagram:',
            'instagram :', 'instagram.', 'instagram;', 'instagram ;',
            'instragram ', 'instragram -', 'instragram-', 'instragram:',
            'instragram :', 'instragram.', 'instragram;', 'instragram ;',
            'insta ', 'insta -', 'insta-', 'insta:', 'insta :', 'insta.', 'insta;', 'insta ;', 'insta@',
        ]
        for tag in tags:
            pos = find_ig_in_text(line, tag)
            if pos > 0:
                return parse_ig_line(line[pos:])

    return ig


if __name__ == '__main__':
    bio_ = """Insta : myigdddd
    """
    ig_username = parse_bio(bio_)
    print(ig_username)

    with open('profiles.txt', 'r') as f:
        lines = f.readlines()
        with open('profiles_parsed_ig.txt', 'w') as out:
            for profile_line in lines:
                profile = json.loads(profile_line)
                profile['instagram'] = parse_bio(profile['bio'])
                out.write(json.dumps(profile) + '\n')
