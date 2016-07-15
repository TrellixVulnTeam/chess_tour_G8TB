from channels import route
from .consumers import *


# There's no path matching on these routes; we just rely on the matching
# from the top-level routing. We _could_ path match here if we wanted.
websocket_routing = [
    # Called when WebSockets connect
    route("websocket.connect", ws_connect),

    # Called when WebSockets get sent a data frame
    route("websocket.receive", ws_receive),

    # Called when WebSockets disconnect
    route("websocket.disconnect", ws_disconnect),
]


# You can have as many lists here as you like, and choose any name.
# Just refer to the individual names in the include() function.
custom_routing = [
    # Handling different chat commands (websocket.receive is decoded and put
    # onto this channel) - routed on the "command" attribute of the decoded
    # message.
    route("round.receive", round_join, command="^join$"),
    route("round.receive", round_leave, command="^leave$"),
    route("round.receive", piece_move, command="^make_move$"),
    route("round.receive", round_check, command="^check$"),
    route("round.receive", timer_down_to_start, command="^timer_down$"),
    route("round.receive", get_PGN, command="^PGN$"),
    route("round.receive", close_round, command="^game_over$"),
]
