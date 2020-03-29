def country_pattern(info):
    return (
        f"*{info['country']}*\n"
        f"Всего: {info['total_cases']}\n"
        f"Новые случаи: {info['new_cases']}\n"
        f"Погибшие: {info['total_deaths']}\n"
        f"Выздоровевшие: {info['recovered_cases']}"
    )
