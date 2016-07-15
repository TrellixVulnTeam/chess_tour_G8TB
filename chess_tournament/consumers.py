import json, time
from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from .settings import MSG_TYPE_LEAVE, MSG_TYPE_ENTER, NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS
from .models import Round, Tournament
from .utils import *
from .exceptions import ClientError


### WebSocket handling ###


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    # Initialise their session
    message.channel_session['rounds'] = []
    message.channel_session['timer'] = 0

# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("round.receive").send(payload)


@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    for room_id in message.channel_session.get("round", set()):
        try:
            room = Round.objects.get(pk=room_id)
            # Removes us from the room's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            room.websocket_group.discard(message.reply_channel)
        except Round.DoesNotExist:
            pass


### Chat channel handling ###


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
@catch_client_error
def round_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    room = get_room_or_error(message["room"], message.user)
    room.connectUser(message["room"], message.user)
    # Send a "enter message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_ENTER)

    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the chat room gets them.
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rounds'] = list(set(message.channel_session['rounds']).union([room.id]))
    # Send a message back that will prompt them to open the room
    # Done server-side so that we could, for example, make people
    # join rooms automatically.
    cur_timer = room.time_player_1 if room.player_1 == message.user else room.time_player_2
    op_timer = room.time_player_1 if room.player_1 != message.user else room.time_player_2

    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.name,
            "time": [op_timer if op_timer != 0 else room.tour.roundTimeLimit * 60 * 100, cur_timer if cur_timer != 0 else room.tour.roundTimeLimit * 60 * 100]
        }),
    })


@channel_session_user
@catch_client_error
def round_leave(message):
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)
    room.disconnectUser(message["room"], message.user)
    # Send a "leave message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_LEAVE)

    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rounds'] = list(set(message.channel_session['rounds']).difference([room.id]))
    # Send a message back that will prompt them to close the room
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })


@channel_session_user
@catch_client_error
def piece_move(message):
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rounds']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # Find the room they're sending to, check perms
    room = get_room_or_error(message["room"], message.user)

    # Send the message along
    room.updateGame(message["pgn"], message["turn"], message.user)

@channel_session_user
@catch_client_error
def close_round(message):
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rounds']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # Find the room they're sending to, check perms
    room = get_room_or_error(message["room"], message.user)
    room.winnerId = int(message["winner"])
    room.is_finished = True
    room.save()
    # Send the message along
    room.send_message(int(room.winnerId), message.user, 8)

@channel_session_user
@catch_client_error
def round_check(message):
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rounds']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # Send the message along
    room = get_room_or_error(message["room"], message.user)
    room.updateTimer(message['timer'], message.user)

    cur_timer = room.time_player_1 if room.player_1 == message.user else room.time_player_2
    op_timer = room.time_player_1 if room.player_1 != message.user else room.time_player_2
    message.reply_channel.send({
        "text": json.dumps({
            "ready": user_is_connected(message["room"], message["op_user"]),
            "uid": message["op_user"],
            "time": [op_timer if op_timer != 0 else room.tour.roundTimeLimit * 60 * 100, cur_timer if cur_timer != 0 else room.tour.roundTimeLimit * 60 * 100]
        }),
    })

@channel_session_user
@catch_client_error
def get_PGN(message):
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rounds']:
        raise ClientError("ROOM_ACCESS_DENIED")
     # Find the room they're sending to, check perms
    room = get_room_or_error(message["room"], message.user)
    # Send the message along
    message.reply_channel.send({
        "text": json.dumps({
            "pgn": room.PGN
        }),
    })

@channel_session_user
@catch_client_error
def timer_down_to_start(message):
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rounds']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # Send the message along
    room = get_room_or_error(message["room"], message.user)
    # Send the message along
    start = time.time()
    time.clock()    
    elapsed = 0
    while elapsed < message['seconds']:
        elapsed = time.time() - start
        room.send_message(elapsed, message.user,6)
        time.sleep(1)