import os
import requests

ACCESS_TOKEN = None


def authenticate():
    auth = (os.getenv("WCL_CLIENT_ID"), os.getenv("WCL_CLIENT_SECRET"))
    response = requests.post(
        "https://www.warcraftlogs.com/oauth/token",
        data={"grant_type": "client_credentials"},
        auth=auth,
    )
    if response.status_code == 200:
        global ACCESS_TOKEN
        ACCESS_TOKEN = response.json()["access_token"]
    else:
        raise Exception(f"Could not authenticate: {response}")


def query(query):
    response = requests.post(
        "https://www.warcraftlogs.com/api/v2/client",
        json={
            "query": query,
        },
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
    )
    if response.json().get("data"):
        return response
    raise Exception(response.text)


def fetch_report(report_id):
    response = query(
        f"""
    query getReport {{
        reportData{{
            report(code: "{report_id}")
            {{
                code
                endTime
                startTime
                title
                zone
                {{
                    id
                }}
                masterData
                {{
                    lang
                    abilities
                    {{
                        gameID
                        type
                    }}
                    actors
                    {{
                        gameID
                        name
                        petOwner
                        type
                        subType
                    }}
                }}
                fights(killType: Encounters)
                {{
                    encounterID
                    startTime
                    endTime
                    name
                    enemyNPCs
                    {{
                        gameID
                        id
                        instanceCount
                        groupCount
                    }}
                    friendlyPlayers
                    fightPercentage
                    kill
                }}
            }}
        }}
    }}
    """
    )
    return response.json()["data"]["reportData"]["report"]


def fetch_reports(guild_id, start_time, end_time):
    response = query(
        f"""
    query getReport {{
        reportData{{
            reports(guildID: {guild_id}, startTime: {start_time}, endTime: {end_time}, limit: 100)
            {{
                data
                {{
                    code
                }}
            }}
        }}
    }}
    """
    )
    return response.json()["data"]["reportData"]["reports"]["data"]
