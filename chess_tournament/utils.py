from .exceptions import ClientError
from .models import Round, Chess


def catch_client_error(func):
    """
    Decorator to catch the ClientError exception and translate it into a reply.
    """
    def inner(message):
        try:
            return func(message)
        except ClientError as e:
            # If we catch a client error, tell it to send an error string
            # back to the client on their reply channel
            e.send_to(message.reply_channel)
    return inner


def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated():
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        room = Round.objects.get(pk=room_id)
    except Round.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    return room

def user_is_connected(room_id, _user):
    try:
        chess = Chess.objects.get(user = _user,in_progress = room_id)
    except:
        chess = None
    if chess is not None:
        return chess.is_connected
    else:
        return False
