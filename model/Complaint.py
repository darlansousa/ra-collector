import json


class Complaint:
    def __init__(self, cod, identifier, title, date, chanel, reason, description, complainer):
        self.cod = cod
        self.identifier = identifier
        self.title = title
        self.date = date
        self.chanel = chanel
        self.reason = reason
        self.description = description
        self.complainer = complainer

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
