import api
import json


def team_display():
    team_services = api.pull_machines()
    if team_services:
        for team in team_services:
            print(f"team_id: {team["team_id"]}\n"
                  f"service_id: {team["service_id"]}\n"
                  f"service_name: {team["service_name"]}\n"
                  f"hostname: {team["hostname"]}\n")

        with open("team_data/team_data.json", "w") as f:
            json.dump(team_services, f, indent=2)


def flag_display():
    flags = api.pull_flag_id()
    if flags:
        for flag in flags:
            print(f"flag_id: {flag["flag_id"]}\n"
                  f"team_id: {flag["team_id"]}\n"
                  f"service_id: {flag["service_id"]}\n"
                  f"tick: {flag["tick"]}\n"
                  f"expiration: {flag["expiration"]}\n"
                  f"hostname: {flag["hostname"]}\n"
                  )
        with open("flag_data/flag_data.json", "w") as f:
            json.dump(flags, f, indent=2)


def submissions_display():
    subs = api.pull_submissions()
    if subs:
        for sub in subs:
            print(f"flag: {sub["flag"]}\n"
                  f"team_id: {sub["team_id"]}\n"
                  f"service_id: {sub["service_id"]}\n"
                  f"tick: {sub["tick"]}\n"
                  f"timestamp: {sub["timestamp"]}\n")
