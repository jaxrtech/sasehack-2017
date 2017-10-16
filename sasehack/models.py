
class FollowupEvent:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data


class Response:
    def __init__(self, text=None, followup_event=None):
        self.speech = text
        self.display_text = text
        self.followup_event = followup_event


class UserInput:
    def __init__(self, message: str, session_id: str, params: dict, text: str, action: str, intent: str):
        self.message = message
        self.session_id = session_id
        self.params = params
        self.raw = text
        self.action = action
        self.intent = intent

