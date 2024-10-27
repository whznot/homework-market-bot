from dateparser import parse
import locale


locale.setlocale(locale.LC_TIME, 'ru-RU')


def parse_user_date(date_str):
    parsed_date = parse(date_str, languages=['ru'])

    if not parsed_date:
        return None

    if parsed_date.tzinfo is not None:
        parsed_date = parsed_date.replace(tzinfo=None)

    return parsed_date.strftime("%A, %d.%m %H:%M")
