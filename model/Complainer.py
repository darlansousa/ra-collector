import json


class Complainer:
    def __init__(self, cpf, name, city, email, phone, phone2, phone3, is_client, uc):
        self.cpf = cpf
        self.name = name
        self.city = city
        self.email = email
        self.phone = phone
        self.phone2 = phone2
        self.phone3 = phone3
        self.is_client = is_client
        self.uc = uc

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
