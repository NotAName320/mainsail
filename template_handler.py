from nsdotpy.session import NSSession


def template_handler(text: str, client: NSSession):
    text = text.lower().replace('_', ' ').replace(f'[nation]{client.nation.lower().replace("_", " ")}[/nation]', '[bot_nation]')
    return text
