import api

class MissingFlagException(Exception):
    pass

class Flag:
    def __init__(self, fid: str, team_id: int, service_id: int, tick: int, expiration: int, hostname: str):
        self.fid = fid
        self.team_id = team_id
        self.service_id = service_id
        self.tick = tick
        self.expiration = expiration
        self.hostname = hostname
        self.key = None

    def __str__(self):
        return f"FID: {self.fid}, HOSTNAME: {self.hostname}"

    def __repr__(self):
        return f"FID: {self.fid}, HOSTNAME: {self.hostname}"

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