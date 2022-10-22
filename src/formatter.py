def tags_to_teams(tags):
    tags = tags.split(',')
    t1 = strip_tags(tags[0].split())
    t2 = strip_tags(tags[1].split())
    return t1, t2


def tag_to_id(tag):
    tag = tag.strip()
    return extract_id(tag)


def strip_tags(team):
    return [extract_id(player) for player in team]


def add_tags(player_id):
    return f'<@{player_id}>'


def extract_id(player_tag):
    return player_tag[2:-1]
