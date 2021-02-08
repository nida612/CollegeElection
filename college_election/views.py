import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from college_election.forms import *
from college_election.models import *

election_post_titles = ['President', 'Vice President', 'Cultural Secretary', 'General Secretary', 'Treasurer']


def index(request):
    user = request.user
    if user and user.is_authenticated:
        if Staff.objects.filter(user=user).exists():
            return redirect('staff_dashboard')
        elif Student.objects.filter(user=user).exists():
            return redirect('student_dashboard')
    return render(request, 'college_election/index.html')


@csrf_exempt
def staff_login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'college_election/staff_login.html', context={'form': form})
    else:
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        user = authenticate(username=user_id, password=password)
        if user is not None:
            if Staff.objects.filter(user_id=user_id).exists():
                login(request, user)
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Invalid, user not An Admin.')
                form = LoginForm()
                return render(request, 'college_election/staff_login.html', context={'form': form})
        else:
            messages.error(request, 'Invalid Credentials.')
            form = LoginForm()
            return render(request, 'college_election/staff_login.html', context={'form': form})


def staff_dashboard(request):
    if request.user and request.user.is_authenticated and Staff.objects.filter(user=request.user):
        allElec = Election.objects.all()
        candidates = Candidate.objects.filter(status='Waiting')
        filtered_candidates = []

        for i in range(len(candidates)):
            if candidates[i].position.election.status == 'Registration Open':
                filtered_candidates.append(candidates[i])

        return render(request, 'college_election/staff_dashboard.html',
                      context={'allElec': allElec, 'candidates': filtered_candidates})
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def logoutUser(request):
    logout(request)
    return redirect('index')


def election(request):
    if request.user and request.user.is_authenticated and request.method == 'GET':
        form = ElectionInfoForm(initial={'voting_start': datetime.now() + timedelta(days=1),
                                         'voting_end': datetime.now() + timedelta(days=2)})
        return render(request, 'college_election/election.html', context={'form': form})
    else:
        form = ElectionInfoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                try:
                    form_election = form.save()
                    saved_election = Election.objects.get(title=form_election.title)
                    for pos_title in election_post_titles:
                        pos = Position()
                        pos.title = pos_title
                        pos.election = saved_election
                        pos.save()
                    messages.success(request, 'Election Created Successfully')
                except Exception as e:
                    print(e)

        else:
            messages.error(request, form.errors)
            print(form.errors)

        return redirect('staff_dashboard')


def staff_election_dashboard(request, election_id):
    if request.user and request.user.is_authenticated and Staff.objects.filter(user=request.user):
        election = Election.objects.get(election_id=election_id)
        positions = election.position_set.all()
        pos_candi_map = {}
        for pos in positions:
            pos_candi_map[pos] = {x: {} for x in Candidate.objects.filter(position=pos, status='Approved').all()}
        result_map = results(election)
        for pos, candis in result_map.items():
            for candi, candi_res in candis.items():
                pos_candi_map[pos][candi] = candi_res
        return render(request, 'college_election/staff_election_dashboard.html',
                      context={'election': election, 'posCandiMap': pos_candi_map})
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def candidate_approval(request, candidate_id, app_id):
    if request.user and request.user.is_authenticated and Staff.objects.filter(user=request.user):
        candidate = Candidate.objects.get(id=candidate_id)
        if app_id == 1:
            candidate.status = 'Approved'
        elif app_id == 2:
            candidate.status = 'Rejected'

        candidate.save()
        return redirect('index')
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def student_login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'college_election/student_login.html', context={'form': form})
    else:
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        user = authenticate(username=user_id, password=password)
        if user is not None:
            if Student.objects.filter(user_id=user_id).exists():
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid, user not A Student.')
                form = LoginForm()
                return render(request, 'college_election/student_login.html', context={'form': form})
        else:
            messages.error(request, 'Invalid Credentials.')
            form = LoginForm()
            return render(request, 'college_election/student_login.html', context={'form': form})


def student_dashboard(request):
    if request.user and request.user.is_authenticated and Student.objects.filter(user=request.user):
        allElec = Election.objects.all()
        candidates = Candidate.objects.filter(student__user=request.user)
        filtered_candidates = []

        for i in range(len(candidates)):
            if candidates[i].position.election.status == 'Registration Open':
                filtered_candidates.append(candidates[i])
        return render(request, 'college_election/student_dashboard.html',
                      context={'allElec': allElec, 'candidates': filtered_candidates})
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def student_election_dashboard(request, election_id):
    if request.user and request.user.is_authenticated and Student.objects.filter(user=request.user):
        election = Election.objects.get(election_id=election_id)
        positions = election.position_set.all()
        pos_candi_map = {}
        for pos in positions:
            pos_candi_map[pos] = {x: {} for x in Candidate.objects.filter(position=pos, status='Approved').all()}
        result_map = results(election)
        for pos, candis in result_map.items():
            for candi, candi_res in candis.items():
                pos_candi_map[pos][candi] = candi_res
        return render(request, 'college_election/student_election_dashboard.html',
                      context={'election': election, 'posCandiMap': pos_candi_map})
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def register_candidate(request, position_id):
    student = Student.objects.get(user=request.user)
    if request.user and request.user.is_authenticated and student:
        position = Position.objects.get(id=position_id)
        if position:
            if position.election.status == 'Registration Open':
                try:

                    Candidate.objects.create(position=position, student=student)
                except IntegrityError as e:
                    messages.error(request, 'Already Applied')
                    return redirect('index')
                else:
                    messages.success(request, "Request Successfully Created. Waiting for Staff to Approve!")
                    return redirect('index')
            else:
                messages.error(request, 'Registrations Closed')
                return redirect('index')
        else:
            messages.error(request, 'Position Does not exist')
            return redirect('student_election_dashboard')
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def activate_election(request, election_id):
    if request.user and request.user.is_authenticated and Staff.objects.filter(user=request.user):
        election = Election.objects.get(election_id=election_id)
        if election:
            election.voting_start = datetime.today()
            election.save()
        else:
            messages.error(request, 'Election not found!')
        return redirect('index')
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def deactivate_election(request, election_id):
    if request.user and request.user.is_authenticated and Staff.objects.filter(user=request.user):
        election = Election.objects.get(election_id=election_id)
        if election:
            election.voting_end = datetime.today()
            election.save()
        else:
            messages.error(request, 'Election not found!')
        return redirect('index')
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return redirect('index')


def already_voted(candi_ids, student_id):
    elections = Election.objects.filter(position__candidate__id__in=candi_ids).distinct()
    if Vote.objects.filter(voter__user_id=student_id, candidate__position__election__in=elections).exists():
        return True
    return False


@csrf_exempt
def submit_vote(request):
    student = Student.objects.get(user=request.user)
    if request.user and request.user.is_authenticated and student:
        votes = []
        for item in request.POST:
            value = request.POST.get(item)
            if value:
                votes.append(value)
            else:
                messages.error(request, 'Not voted for all positions!')
                return HttpResponse(json.dumps({'status': 0, 'message': 'Not voted for all positions!'}))
        if not already_voted(votes, student.user_id):
            with transaction.atomic():
                try:
                    for candi_id in votes:
                        vote = Vote.objects.create(voter=student, candidate_id=candi_id)
                    messages.success(request, 'Successfully voted!!')
                except IntegrityError as e:
                    print(e)
                    return HttpResponse(json.dumps({'status': 0, 'message': 'Already Voted!'}))
                else:
                    return HttpResponse(json.dumps({'status': 1, 'message': 'Voted Successfully!'}))
        else:
            return HttpResponse(json.dumps({'status': 0, 'message': 'Already Voted!'}))
    else:
        messages.error(request, 'You Are Not Authorized To Access That Page')
        return HttpResponse(json.dumps({'status': 0, 'message': 'You Are Not Authorized To Access That Page'}))


def results(election):
    if election.status == 'Archived':
        votes = Vote.objects.filter(candidate__position__election=election)
        positions = election.position_set.all()
        vote_map = {x: [] for x in positions}
        posCandiMap = {x: x.candidate_set.all() for x in positions}

        # counting votes
        for vote in votes:
            position = vote.candidate.position
            candidate = vote.candidate
            vote_map[position].append(candidate)

        response = {}
        # response contains vote count of each candidate for each position
        # eg {position:{candidate:(vote_count, 0)}}
        for pos, candis in posCandiMap.items():
            response[pos] = {}
            for candi in candis:
                candi_vote_count = len([x for x in vote_map[pos] if x == candi])
                response[pos][candi] = (candi_vote_count, -1)

        result = {}
        # update response with winner of each position
        for pos, candis in response.items():
            max_votes = max([x[0] for x in candis.values()])
            winner_exists = True if len([x[0] for x in candis.values() if x[0] == max_votes]) == 1 else False
            result[pos] = {}
            for candi, candi_res_tuple in candis.items():
                candi_vote_count = candi_res_tuple[0]
                if winner_exists and candi_vote_count == max_votes:
                    result[pos][candi] = (candi_vote_count, 1)
                elif not winner_exists and candi_vote_count == max_votes:
                    result[pos][candi] = (candi_vote_count, 0)
                else:
                    result[pos][candi] = (candi_vote_count, -1)

        return result
    else:
        return {}
