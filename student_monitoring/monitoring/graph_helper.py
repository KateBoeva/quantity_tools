from requests_oauthlib import OAuth2Session
from monitoring.models import Participant

graph_url = 'https://graph.microsoft.com/v1.0'
graph_url_beta = 'https://graph.microsoft.com/beta'


def get_user(token):
    graph_client = OAuth2Session(token=token)
    user = graph_client.get('{0}/me'.format(graph_url))

    return user.json()


def get_teams_user_activity_user(token):
    graph_client = OAuth2Session(token=token)

    query_params = {
        '$format': 'application/json'
    }

    events = graph_client.get("{0}/reports/getTeamsUserActivityUserDetail(period='D7')".format(graph_url), params=query_params)
    return events.json()


def get_teacher_info(token):
    graph_client = OAuth2Session(token=token)
    teacher_info = graph_client.get("{0}/me".format(graph_url)).json()

    return {
        "id": teacher_info['id'],
        "name": teacher_info['displayName']
    }


def get_team_members(token, team_id):
    graph_client = OAuth2Session(token=token)
    members_info = graph_client.get("{0}/groups/{1}/members".format(graph_url, team_id)).json()
    members = []
    for member in members_info['value']:
        if Participant.objects.filter(teams_id=member['id']).exists():
            p = Participant.objects.get(teams_id=member['id'])
        else:
            p = Participant(teams_id=member['id'], name=member['displayName'])
            p.save()
        members += [p]

    return members


def get_team_info(token, name):
    graph_client = OAuth2Session(token=token)
    teams_info = graph_client.get("{0}/me/joinedTeams".format(graph_url)).json()

    for team in teams_info['value']:
        if name in team['displayName']:
            return {
                "id": team["id"],
                "name": team["displayName"],
                "webUrl": team["webUrl"]
            }

    return None


def get_meetings_list(token, name):
    graph_client = OAuth2Session(token=token)
    meetings = graph_client.get("{0}/me/onlineMeetings".format(graph_url)).json()
    teams_info = get_team_info(token,name)

    result = []

    for meeting in meetings['value']:
        if meeting['team'] == teams_info['id']:
            result += [meeting]

    return meetings


def get_calls_info(token, name):
    graph_client = OAuth2Session(token=token)
    teams_info = graph_client.get("{0}/me/joinedTeams".format(graph_url)).json()
    meetings = get_meetings_list(token, name)

    calls = []
    for meeting in meetings:
        members = []
        ps = graph_client.get("{0}/meetings/{1}/participants".format(graph_url, meeting['id'])).json()
        for p in ps:
            members += [{
                "id": p["id"],
                "mutePercent": p["caller_audio_MediaLine_OutboundStream_Payload_Audio_SendMutePercent"],
                "startDateTime": p["startDateTime"],
                "endDateTime": p["endDateTime"],
                "sharingPercent": p["caller_audio_MediaLine_OutboundStream_SendDemostrationFilesPercent"]
            }]
        calls += [{
            "id": meeting["id"],
            "startDateTime": meeting["startDateTime"],
            "endDateTime": meeting["endDateTime"],
            "participants": members
        }]

    return None

