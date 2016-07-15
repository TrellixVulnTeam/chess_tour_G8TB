from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator

from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives, send_mail

from django.template import loader, RequestContext, Context
from django.template.loader import get_template

from django.shortcuts import render_to_response, render
from django.db.models.query_utils import Q

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from datetime import datetime, timedelta
from django.conf import settings
from pytz import timezone

import re

from chess_tournament.models import *

def UserActivity(func):
    def wrapped(request, **kargs):
        if request.user.is_authenticated():
            _user = request.user
            _date = datetime.now(timezone(settings.TIME_ZONE))

            try:
                ch_board = _user.chess_board
            except:
                ch_board = None

            if ch_board is None:
                chess_user = Chess(user = _user, last_activity = _date)
                chess_user.save()
            else:
                chess_user = Chess.objects.get(user = _user)
                chess_user.last_activity = _date
                chess_user.save()
        return func(request, **kargs)
    return wrapped

@UserActivity
def UpdateOnlainUser(request):
    pass

def who_online(request):
    if request.GET.get('update'):
        try:
            UpdateOnlainUser(request)
            updated = True
        except:
            updated = False
        return JsonResponse({'is_updated':updated})
    if request.GET.get('get_list'):
        _date = datetime.now(timezone(settings.TIME_ZONE)) - timedelta(minutes=10)
        users_list = Chess.objects.filter(last_activity__gte=_date)
        res_object = {}
        for ch_users in users_list:
            res_object[ch_users.user.username] = ch_users.last_activity
        return JsonResponse(res_object)


@UserActivity
def index(request):
    return render(request, 'chtor/index.html', {
            'group': request.user.groups.values_list('name',flat=True),
            'bt_active':'tour',
            'tournaments': Tournament.objects.filter(is_finished=False)[:5]
            })

def ger_round_by_tour_id(request, _tour_id):
    rounds = Round.objects.filter(tour=_tour_id)
    for _round in rounds:
        if _round.player_1 == request.user or _round.player_2 == request.user:
            del rounds
            rounds = _round
    return rounds

@UserActivity
def tournament(request, _tour_id = None):
    rounds = ger_round_by_tour_id(request, _tour_id)    
    return render(request, 'chtor/tournament.html', {
            'tour': Tournament.objects.get(pk=_tour_id),
            'opponent_user': rounds.player_1 if rounds.player_1 != request.user else rounds.player_2,
            'current_user': rounds.player_1 if rounds.player_1 == request.user else rounds.player_2,
            'white': 'true' if rounds.player_1 == request.user else 'false',
            'round': rounds
            })

@UserActivity
def tournament_api(request, _tour_id = None):
    if request.method == "POST":
        _round = ger_round_by_tour_id(request, _tour_id)
        gen_str = "|".join(request.POST[_post_] for _post_ in request.POST.dict() if _post_ not in 'csrfmiddlewaretoken')+'##'
        _round.History += gen_str
        _round.save()
    return HttpResponse(gen_str)

@UserActivity
def new_tor(request):
    return render(request, 'chtor/new_tournament.html', {
            'group': request.user.groups.values_list('name',flat=True),
            'bt_active':'new_tour'
            })

def auth(request, evt = 'login', uidb64=None, token=None):
    def _in():
        ''' subfunction used to login '''
        if request.method == "POST":
            if all(request.POST[x] for x in request.POST.dict()):
                user = authenticate(username=request.POST['login'], password=request.POST['password'])
                if user is not None:
                    # the password verified for the user
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect(reverse('chtor:index'))
                    else:
                        messages.error(request, 'The password is valid, but the account has been disabled!')
                        return render(request, 'chtor_admin/login.html')
                else:
                    # the authentication system was unable to verify the username and password
                    messages.error(request, 'The username and password were incorrect.')
                    return render(request, 'chtor_admin/login.html')
            else:
                messages.error(request, 'One or more field\'s are empty.')
                return render(request, 'chtor_admin/login.html')
        else:
            return render(request, 'chtor_admin/login.html')

    def _up(error_message=''):
        ''' subfunction used to signup '''
        if request.method == "POST":
            if all(request.POST[x] for x in request.POST.dict()):
                messages.error(request, 'One or more field\'s are empty.')
                return render(request, 'chtor_admin/signup.html')
            else:
                messages.error(request, 'One or more field\'s are empty.')
                return render(request, 'chtor_admin/signup.html')
        else:
            return render(request, 'chtor_admin/signup.html')

    def _reset_password(error_message=''):
        ''' subfunction used to reset password '''
        if request.method == "POST" and request.POST['reset_pass']:
            if not request.POST['reset_email']:
                error_message = 'Email field are empty.'
            else:
                associated_users= User.objects.filter(Q(email=request.POST['reset_email'])|Q(username=request.POST['reset_email']))
                if associated_users.exists():
                    for user in associated_users:
                        email_temp_data = Context({
                                'email': user.email,
                                'domain': request.META['HTTP_HOST'],
                                'site_name': '127.0.0.2:8000',
                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                'time': urlsafe_base64_encode(force_bytes(datetime.now())),
                                'user': user,
                                'token': default_token_generator.make_token(user),
                                'protocol': 'http',
                                })
                        text_subject = get_template('chtor_admin/_res_/reset_subject.txt').render()
                        html_content = get_template('chtor_admin/_res_/reset_email.html').render(email_temp_data)
                        msg = EmailMultiAlternatives(text_subject, html_content, 'vselochi9@yandex.ru', [request.POST['reset_email']])
                        msg.content_subtype = "html"
                        msg.send()
                        messages.error(request, error_message)
                        return render(request, 'chtor_admin/reset_password_done.html', {
                                'email': user.email
                                })
                else:
                    messages.error(request, 'This username does not exist in the system.')
                    return render(request, 'chtor_admin/reset_password.html')
                # send_mail('Subject here', 'Here is the message.', 'vselochi4@yandex.ru', [request.POST['reset_email']], fail_silently=False)
        messages.error(request, error_message)
        return render(request, 'chtor_admin/reset_password.html')

    def _confirm_reset_password(error_message=''):
        ''' subfunction used to set new password '''
        if request.method == "POST":
            if request.POST['new_pass'] == request.POST['c_new_pass']: 
                if all(request.POST[x] for x in request.POST.dict()):
                    uidb64_l = uidb64.split(':')
                    time_now = datetime.now()
                    time_old = datetime.strptime(str(urlsafe_base64_decode(uidb64_l[1]), 'utf-8'), '%Y-%m-%d %H:%M:%S.%f')
                    if 0 < (time_now-time_old).seconds < 3600:
                        try:
                            uid = urlsafe_base64_decode(uidb64_l[0])
                            user = User.objects.get(id=uid)
                        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                            user = None
                            time_old = time_now
                        if user is not None and default_token_generator.check_token(user, token):
                            user.set_password(request.POST['new_pass'])
                            user.save()
                            messages.error(request, 'Password has been reset.')
                            return render(request, 'chtor_admin/confirm_reset_password.html')
                        else:
                            messages.error(request, 'The reset password link is no valid.')
                            return render(request, 'chtor_admin/confirm_reset_password.html')
                    else:
                        messages.error(request, 'The reset password link is no longer valid.')
                        return render(request, 'chtor_admin/confirm_reset_password.html')
                else:
                    messages.error(request, 'One or more field\'s are empty.')
                    return render(request, 'chtor_admin/confirm_reset_password.html')
            else:
                messages.error(request, 'Password and Confirm Password is not match.')
                return render(request, 'chtor_admin/confirm_reset_password.html')
        else:
            messages.error(request, error_message)
            return render(request, 'chtor_admin/confirm_reset_password.html', {
                    'hash': uidb64,
                    'token':token
                    })
    def _out():
        _date = datetime.now(timezone(settings.TIME_ZONE)) - timedelta(minutes=15)
        chess_user = Chess.objects.get(user = request.user)
        chess_user.last_activity = _date
        chess_user.save()
        logout(request)
        if request.method != "POST":
            return HttpResponseRedirect(reverse('chtor:index'))

    run_evt = {'login': _in, 'logout': _out, 'signup': _up, 'reset_password': _reset_password, 'confirm_reset_password': _confirm_reset_password}

    if evt in run_evt and not request.user.is_authenticated() or evt == 'logout':
        return run_evt[evt]()  
    else:
        return HttpResponseRedirect(reverse('chtor:index'))
        
