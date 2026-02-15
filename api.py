import requests
import json
import os

TOKEN = "e7a9f3c045894d12"

def ensure_data_dirs():
    os.makedirs("flag_data", exist_ok=True)
    os.makedirs("team_data", exist_ok=True)

def pull_machines() -> dict | None:
    """
    Connects to CTF API to pull down machine data for teams
    :return: dict | Team machine data
    """
    url = "https://api.ad.mctf.io/endpoints"
    headers = {"team-token": TOKEN}
    res = requests.get(url=url, headers=headers)
    if res.status_code == 200:
        print("Machine Data Collected")
        return res.json()
    print("Machine Data Failure")
    return None


def pull_flag_ids() -> dict | None:
    """
    Connects to CTF API to pull down flag data for all teams except ours
    :return: dict | Team flag data
    """
    url = "https://api.ad.mctf.io/live_flags"
    headers = {"team-token": TOKEN}
    res = requests.get(url=url, headers=headers)
    if res.status_code == 200:
        print("Flag Data Collected")
        return res.json()
    print("Flag Data Failure")
    return None

def submit_flag(flag: str) -> dict | None:
    """
    Sends flag data to server
    :param flag: | Flag value
    :return: None
    """
    url = "https://api.ad.mctf.io/submit"
    headers = {"team-token": TOKEN}
    payload = {"flag_in": flag}
    res = requests.post(url, data=payload, headers=headers)

    if res.status_code == 200:
        print("Flag Submitted")
        return res.json()
    print("Flag Submission Failed")
    return None

def pull_submissions() -> dict | None:
    """
    Pulls team submission data
    :return: dict | Submission Data
    """
    url = "https://api.ad.mctf.io/submissions"
    headers = {"team-token": TOKEN}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        print("Submissions Pulled")
        return res.json()
    print("Submission Pull Error")
    return None

def team_display():
    team_services = pull_machines()
    if team_services:
        for team in team_services:
            print(f"team_id: {team["team_id"]}\n"
                  f"service_id: {team["service_id"]}\n"
                  f"service_name: {team["service_name"]}\n"
                  f"hostname: {team["hostname"]}\n")

        with open("team_data/team_data.json", "w") as f:
            json.dump(team_services, f, indent=2)

def flag_display():
    flags = pull_flag_ids()
    if flags:
        for flag in flags:
            print(f"flag_identifier: {flag["flag_identifier"]}\n"
                  f"team_id: {flag["team_id"]}\n"
                  f"service_id: {flag["service_id"]}\n"
                  f"tick: {flag["tick"]}\n"
                  f"expiration: {flag["expiration"]}\n"
                  f"hostname: {flag["hostname"]}\n"
                  )
        with open("flag_data/flag_data.json", "w") as f:
            json.dump(flags, f, indent=2)

def submissions_display():
    subs = pull_submissions()
    if subs:
        for sub in subs:
            print(f"flag: {sub["flag"]}\n"
                  f"team_id: {sub["team_id"]}\n"
                  f"service_id: {sub["service_id"]}\n"
                  f"tick: {sub["tick"]}\n"
                  f"timestamp: {sub["timestamp"]}\n")

if __name__ == "__main__":
    ensure_data_dirs()
    sv_flags = []
    flags = pull_flag_ids()
    for r in flags:
        if r["service_id"] == 3:
            print(r)
            sv_flags.append(f'https://{r["hostname"]}/view_info?email={r["flag_identifier"]}&ssn=opensesame')
    for i in sv_flags:
        print(i)