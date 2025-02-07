import requests

token = ""


def pull_machines() -> dict:
    """
    Connects to CTF API to pull down machine data for teams
    :return: dict | Team machine data
    """
    url = "https://scoreboard.mctf.io:8000/endpoints"
    headers = {"team-token": token}
    res = requests.get(url=url, headers=headers)
    if res.status_code == 200:
        print("Machine Data Collected")
        return res.json()
    print("Machine Data Failure")


def pull_flag_id() -> dict:
    """
    Connects to CTF API to pull down flag data for all teams except ours
    :return: dict | Team flag data
    """
    url = "https://scoreboard.mctf.io:8000/endpoints"
    headers = {"team-token": token}
    res = requests.get(url=url, headers=headers)
    if res.status_code == 200:
        print("Machine Data Collected")
        return res.json()
    print("Flag Data Failure")


def submit_flag(flag: str):
    """
    Sends flag data to server
    :param flag: | Flag value
    :return: None
    """
    url = "https://scoreboard.mctf.io:8000/submit"
    headers = {"team-token": token}
    payload = {"flag_in": flag}
    res = requests.post(url, data=payload, headers=headers)

    if res.status_code == 200:
        print("Flag Submitted")
        return res.json()
    print("Flag Submission Failed")


def pull_submissions():
    """
    Pulls team submission data
    :return: dict | Submission Data
    """
    url = "https://scoreboard.mctf.io:8000/submissions"
    headers = {"team-token": token}
    res = requests.post(url, headers=headers)

    if res.status_code == 200:
        print("Submissions Pulled")
        return res.json()
    print("Submission Pull Error")
