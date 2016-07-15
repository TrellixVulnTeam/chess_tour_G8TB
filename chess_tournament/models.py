import json
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels import Group

from datetime import datetime
from pytz import timezone

from .settings import MSG_TYPE_MESSAGE


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class Chess(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, unique=True, related_name="chess_board")
    last_activity = models.DateTimeField(default=datetime(1970,1,1,0,0,0,0,timezone('UTC')),)
    is_avaliable  = models.BooleanField(default=False,)
    is_connected = models.BooleanField(default=False,)
    in_progress  = models.IntegerField(default=-1,)    
    round_time_left = models.IntegerField(default=-1,)
    elo = models.IntegerField(default=1000,)

    class Meta:
        verbose_name = "Chess"
        verbose_name_plural = "Chess"

    def __str__(self):
        return "chess_"+str(self.user)

class Tournament(models.Model):
    name = models.CharField(max_length=100,)
    date = models.DateField(auto_now_add=True,)
    time = models.TimeField()
    roundTimeLimit = models.IntegerField(default=0,)
    playersCount = models.IntegerField(default=0,)
    is_finished = models.BooleanField(default=False,)

    class Meta:
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"

    def __str__(self):
        return self.name

class Round(models.Model):
    PLAYERS = (
        ('1', 'player_1'),
        ('2', 'player_2'),
    )

    tour = models.OneToOneField(Tournament, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100,)
    player_1 = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user), related_name='pleyer_one')
    player_2 = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user), related_name='pleyer_two')
    white = models.CharField(max_length=1, choices=PLAYERS)
    winnerId = models.IntegerField(default=-1,)
    StartTime = models.TimeField()
    PGN = models.TextField(default="",blank=True)
    stepTimes = models.TextField(default="",blank=True)
    time_player_1 = models.IntegerField(default=0,)
    time_player_2 = models.IntegerField(default=0,)
    turn = models.CharField(max_length=1,)
    is_finished = models.BooleanField(default=False,)


    class Meta:
        verbose_name = "Round"
        verbose_name_plural = "Rounds"

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("round-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'round': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )

    def updateGame(self, pgn, turn, user, msg_type=MSG_TYPE_MESSAGE):
        self.PGN = pgn;
        self.turn = turn;
        self.save()

        final_msg = {'round': str(self.id), 'message': [pgn, self.stepTimes], 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )

    def connectUser(self, room_id, _user):
        chess = Chess.objects.get(user = _user)
        chess.is_connected = True
        chess.in_progress = room_id
        chess.save()

    def disconnectUser(self, room_id, _user):
        chess = Chess.objects.get(user = _user)
        chess.is_connected = False
        chess.in_progress = -1
        chess.save()

    def updateTimer(self, _time, _user):
        if self.player_1 == _user:
            self.time_player_1 = _time
        else:
            self.time_player_2 = _time  
        self.save()

    def __str__(self):
        return str(self.tour)+": "+str(self.name)