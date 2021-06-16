import json
import math
from django.utils.dateparse import parse_datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from monitoring.auth_helper import get_sign_in_url, get_token_from_code, store_token, \
    store_user, remove_user_and_token, get_token
from monitoring.graph_helper import get_user, get_teacher_info, get_team_info, get_team_members
from monitoring.models import Participant, Settings, Team, Meeting, Action


group = ''


def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)

    if error:
        context['errors'] = []
        context['errors'].append(error)

    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context


def sign_in(request):
    sign_in_url, state = get_sign_in_url()
    request.session['auth_state'] = state
    return HttpResponseRedirect(sign_in_url)


def sign_out(request):
    remove_user_and_token(request)

    return HttpResponseRedirect(reverse('home'))


def home(request):
    global group
    if 'group' in request.GET.keys():
        group = request.GET['group']
        request.session['group'] = request.GET['group']

    if 'user' not in request.session.keys():
        return HttpResponseRedirect(reverse('signin'))

    token = get_token(request)
    teacher_info = get_teacher_info(token)
    team = get_team_info(token, group)
    context = initialize_context(request)
    if team and Settings.objects.filter(owner__teams_id=teacher_info['id'], team__teams_id=team['id']).exists():
        request.session['team'] = team['id']
        context.update({"settings": get_settings(request)})
        context.update(calc_stat(request))
        return render(request, "monitoring/general.html", context)

    context.update({"group": group})

    return render(request, 'monitoring/settings_form.html', context)


def set_settings(request):
    context = initialize_context(request)
    token = get_token(request)
    if request.method == "POST":
        if Settings.objects.filter(owner__name=request.session['user']['name']).exists():
            settings = Settings.objects.get(owner__name=request.session['user']['name'])
        else:
            team_info = get_team_info(token, request.POST['team'])
            if Participant.objects.filter(name=request.session['user']['name']).exists():
                teacher = Participant.objects.get(name=request.session['user']['name'])
            else:
                teacher_info = get_teacher_info(token)
                teacher = Participant(teams_id=teacher_info["id"], name=teacher_info['name'], is_teacher=True)
                teacher.save()
            team = Team(teams_id=team_info['id'], name=team_info['name'])
            team.save()
            request.session['team'] = team_info['id']
            settings = Settings(team=team, owner=teacher)

        settings.teacher_presentation = request.POST['teacher-sharing']
        settings.student_presentation = request.POST['student-sharing']
        settings.microphone = request.POST['student-speaking']
        settings.attendance = request.POST['attendance']
        settings.allow_to_miss = request.POST['allow_to_miss']
        settings.active_percent = request.POST['active-percent']
        settings.start = request.POST['start']
        settings.end = request.POST['end']

        settings.save()
        context.update(calc_stat(request))

        return render(request, "monitoring/general.html", context)

    settings = Settings.objects.get(owner__teams_id=request.session['user']['id'])
    return render(request, 'monitoring/settings_form.html', {"settings": settings})


def get_settings(request):
    teacher = Participant.objects.get(teams_id=request.session['user']['id'])
    team = Team.objects.get(teams_id=request.session['team'])
    settings = Settings.objects.get(owner=teacher, team=team)

    return settings


def get_statistics(request):
    context = initialize_context(request)
    context.update({"settings": get_settings(request)})
    return render(request, 'monitoring/statistics.html', context)


def calc_stat(request):
    token = get_token(request)
    team = Team.objects.get(teams_id=request.session['team'])
    members = get_team_members(token, request.session['team'])

    teacher = Participant.objects.get(teams_id=request.session['user']['id'])
    with open('static/calls.json', 'r') as data:
        meetings = json.load(data)
        for meeting in meetings['data']:
            ps = []

            if Meeting.objects.filter(teams_id=meeting["id"]).exists():
                meet = Meeting.objects.get(teams_id=meeting["id"])
            else:
                meet = Meeting(teams_id=meeting["id"], start_time=meeting['startDateTime'], end_time=meeting['endDateTime'], teacher=teacher, team=team)
                meet.save()

            for mem in members:
                if not Action.objects.filter(meeting=meet, participant=mem).exists():
                    a = Action(meeting=meet, participant=mem)
                    a.save()

            for p in meeting["participants"]:
                m = Participant.objects.get(teams_id=p["id"])
                ps += [m]
                time = (parse_datetime(p['endDateTime']) - parse_datetime(p['startDateTime'])).seconds
                presentation = math.trunc(float(p['sharingPercent']) * float(time))
                microphone = math.trunc((1 - float(p['mutePercent'])) * float(time))
                attendance = time
                a = Action.objects.get(meeting=meet, participant=m)
                a.presentation = presentation
                a.microphone = microphone
                a.attendance = attendance
                a.save()
                meet.students.add(m)
            meet.save()
            students = []
            active = 0
            for member in members:
                if not member.is_teacher:
                    status = get_student_status(request, member)
                    students += [{"name": member.name, "teams_id": member.teams_id, "status": status}]
                    if status == "Активен":
                        active += 1

        return {
            "settings": get_settings(request),
            "general": get_general_info(request),
            "teacher": {"name": teacher.name, "teams_id": teacher.teams_id},
            "students": students,
            "activity": {"active": active, "all_count": len(students)}
        }


def get_student_activity(request, student):
    result = {
        "meetings": [],
        "microphone_actives": [],
        "sharing_actives": [],
        "attendance_actives": [],
    }

    meetings = Meeting.objects.filter(teacher__teams_id=request.session['user']['id'])

    for meeting in meetings:
        action = Action.objects.get(meeting=meeting, participant=student)
        result["meetings"] += [meeting.start_time.strftime("%d.%m")]
        result["microphone_actives"] += [action.microphone / 60]
        result["sharing_actives"] += [action.presentation / 60]
        result["attendance_actives"] += [action.attendance / 60]

    return result


def get_student_status(request, student):
    settings = get_settings(request)
    count = Meeting.objects.filter(teacher__teams_id=request.session['user']['id']).count()
    activity = get_student_activity(request, student)

    attendance = 0
    microphone = 0
    presentation = 0

    for key in range(count):
        if activity['attendance_actives'][key] >= settings.attendance:
            attendance += 1

        if activity['microphone_actives'][key] >= settings.microphone:
            microphone += 1

        if activity['sharing_actives'][key] >= settings.student_presentation:
            presentation += 1

    if count - attendance < settings.allow_to_miss or (attendance + microphone + presentation) / (count * 3) < settings.active_percent / 100:
        return "Не активен"

    return "Активен"


def get_participant_info(request, **kwargs):
    context = initialize_context(request)
    student = Participant.objects.get(teams_id=kwargs['teams_id'])

    result = {
        "student": student,
        "status": get_student_status(request, student)
    }

    result.update(get_student_activity(request, student))
    context.update(result)

    if student.is_teacher:
        return render(request, 'monitoring/teacher.html', context)

    return render(request, 'monitoring/student.html', context)


def get_general_info(request):
    context = {
        "meetings": [],
        "microphone_actives": [],
        "sharing_actives": [],
        "attendance_actives": []
    }
    meetings = Meeting.objects.filter(teacher__teams_id=request.session['user']['id'])
    settings = get_settings(request)

    for meeting in meetings:
        if len(meeting.students.all()) > 0:
            microphone_active = 0
            sharing_active = 0
            attendance_active = 0

            for student in meeting.students.all():
                if student.is_teacher:
                    continue

                action = Action.objects.get(meeting=meeting, participant=student)
                if settings.microphone * 60 <= action.microphone:
                    microphone_active += 1
                if settings.student_presentation * 60 <= action.presentation:
                    sharing_active += 1
                if settings.attendance * 60 <= action.attendance:
                    attendance_active += 1

            context["meetings"] += [meeting.start_time.strftime("%d.%m")]
            context["microphone_actives"] += [microphone_active]
            context["sharing_actives"] += [sharing_active]
            context["attendance_actives"] += [attendance_active]

    return context


