import api
import datetime

class MissingFlagException(Exception):
    pass

class Flag:
    def __init__(self, fid: str, team_id: str, service_id: str, tick: str, expiration: datetime.datetime, hostname: str):
        self.id = fid
        self.team_id = team_id
        self.service_id = service_id
        self.tick = tick
        self.expiration = expiration
        self.hostname = hostname
        self.key = None

    def is_expired(self):
        if self.expiration > datetime.datetime.now():
            return True
        return False

    def set_key(self, key: str):
        self.key = key

    def submit(self):
        if self.key is None:
            print(f"[#] Attempted to submit flag with an unset key.")
            return False
        else:
            result = api.submit_flag(self.key)
            if not result:
                print(f"[!] Flag submission failed for flag {self.key}.")
                return False
            else:
                print(f"[$] Flag submission succeeded for flag {self.key}.")
                return True