def country_pattern(info):
    return (
        f"*{info['country']}*\n"
        f"Всего: {info['total_cases']}\n"
        f"Новые случаи: {info['new_cases']}\n"
        f"Погибшие: {info['total_deaths']}\n"
        f"Выздоровевшие: {info['recovered_cases']}"
    )


def rating_pattern(world, info):
    pattern = [
        (str(num+1) + '. ' + country['country'] + ': '
            + str(country['total_cases']))
        for num, country in enumerate(info)
    ]
    pattern = '\n'.join(pattern)
    world_pattern = (
        '*' + world['country'] + ': '
        + str(world['total_cases']) + '*\n\n')
    pattern = world_pattern + pattern
    return pattern
