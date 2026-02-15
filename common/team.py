
class Team:
    def __init__(self, tid: int, service_id: int, service_name: str, hostname: str):
        self.tid = tid
        self.service_id = service_id
        self.service_name = service_name
        self.hostname = hostname