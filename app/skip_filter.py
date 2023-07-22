skip_list = [
    'dy boy', 'trans', 'lesbian', 'transsexual', 'bisexual', 'sexual', 'QUEE',
    'LADYBOY', 'gay', 't girl', 't a girl', 't a real girl', 't real girl', 't real woman',
    '🌈', '🏳️‍🌈', '🏳️‍⚧️', 'LGBTQ', 'lgbtq', 'อวบ', 'อ้วน', 'สาวสอง', 'สอง', 'ไม่ใช่ผ', 'chubby', 'single mom', 'singlemom',
    'แปลงแล้ว', 'pre-op', 'post-op', 'ข้ามเพศ', 'กระเทย', 'เกย์', 'เลสเบี้ยน', 'เลส', 'อ้วน', 'หมี', 'transgender', 'lady',
    'เลสบี้', 'เทย', 'ผญ', 'ผ.ญ.', 'แท้', 'ครับ', 'kub', '🐷', 'Chubby', 'fat', 'แม่เลี้ยง', '🐍', 'big girl', 'Big',
    'thick', 'slender', 'short', 'มีลูก', 'gender', 'non binary', 'non-binary', 'nonbinary', 'ladi', 'bell', 'xx', 'model',
    'ROV', 'PUBG'
]


def should_skip(text: str) -> bool:
    for word in skip_list:
        if word.upper() in text.upper():
            return True
    return False
