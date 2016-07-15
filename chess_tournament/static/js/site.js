$(document).ready(function(){

	// Correctly decide between ws:// and wss://
	var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/api" + window.location.pathname;
    var board,
		game = new Chess(),
		cap_trach = $('.board_capture_trash')
		game_over_paused = true;

	var csrftoken = Cookies.get('csrftoken');

    console.log("Connecting to " + ws_path);

	// connection to socket
    window.socket = new ReconnectingWebSocket(ws_path);
    window.chtor = window.chtor|{}
    // Handle incoming messages

    socket.onmessage = function (message) {
  		// Decode the JSON
  		// console.log("Got websocket message " + message.data);
  		var data = JSON.parse(message.data);
  		// Handle errors
  		if (data.error) {
  			socket.refresh();
  		    console.log(data.error);
  		    return;
  		}
  		// Handle joining
  		if (data.join) {
  		    clearInterval(socketJoinInterval);
  		    console.log("Joining room " + data.join);
  		    chtor.userJoin = true;
  		    socket.send(JSON.stringify({
				    "command": "PGN",
		            "room": chtor.roundId,
				}));
  		    $('.player_info.'+(chtor.white?'w':'b')).find('.timer').attr('timer',data.time[0]).text(timerToString(data.time[0]));
  		    $('.player_info.'+(chtor.white?'b':'w')).find('.timer').attr('timer',data.time[1]).text(timerToString(data.time[1]));
  		} else if (data.pgn || data.pgn == "") {
  			game.clear();
			game.load_pgn(data.pgn)
	  		board.orientation(chtor.white?'white':'black');
			board.position(game.fen());
			BoardCharAddNewLine(0);
			game_over_paused = false
			chtor.hasNoHistory = true
  		} else if (data.ready) {
  		    //console.log("Opponent is ready: " + data.ready);
  		    chtor.opponentUserReady = data.ready;
  		    chtor.oppUserCheckConn += 1;
  		    if(game_over_paused) {
  				game.clear();
				board.position(game.fen());
	  			board.orientation(chtor.white?'white':'black');
	  		}
	  		$('.connect_users .block span').text('Connected').addClass('active');
  		    $('.player_info[userId='+data.uid+'] .player_status').addClass('active');
  		    $('.connect_users button').removeClass('disabled');
  		    $('.player_info.'+(chtor.white?'b':'w')).find('.timer').attr('timer',data.time[0])
  		    if(chtor.oppUserCheckConn == 2 && data.ready)
	  		    socket.send(JSON.stringify({
				    "command": "timer_down",
		            "room": chtor.roundId,
				    "seconds": chtor.startTimer
				}));
  		}  else if (!data.ready) {
  		    //console.log("Opponent is ready: " + data.ready);
  		    chtor.opponentUserReady = data.ready
  		    chtor.oppUserCheckConn += 1;
  		    $('.player_info[userId='+data.uid+'] .player_status').removeClass('active');
  		    $('.player_info[userId='+data.uid+'] .player_status').removeClass('active');

  		    if(chtor.oppUserCheckConn > 15)
  		    	clearInterval(opponentUserReady);
  		} 

  		if (data.leave) {
  			// ЧТО ПРОИСХОДИТ ПРИ ПОКИДАНИИ РАУНДА/ПРОИГРАША ТЕКУЩИМ ИГРОКОМ

  		    console.log("Leaving room " + data.leave);
  		    //$("#room-" + data.leave).remove();
  		    // Handle getting a message
  		} else if (data.message || data.msg_type != 0) {

  			// ОТОБРАЖЕНИЕ ТЕКУЖИХ СООБЩЕНИЙ О ХОДЕ ИГРЫ ИЛИ ПРОИСХОДЯЩИХ СОБЫТИЯХ

  		   
  		    var ok_msg = "";
  		    // msg types are defined in chat/settings.py
  		    // Only for demo purposes is hardcoded, in production scenarios, consider call a service.
  		    

  		    switch (data.msg_type) {
  		        case 0:
  		        	console.log(data)
  		        	clearInterval(opponentUserReady);
  		        	opponentUserReady = setInterval(function(){
					if(chtor.userJoin && chtor.hasNoHistory)
						socket.send(JSON.stringify({
				                "command": "check",
				                "room": chtor.roundId,
				                "op_user": chtor.oppUserId,
				                "timer": $('.player_info.'+(chtor.white?'w':'b')).find('.timer').attr('timer')
				            }));
					}, 500);
					game.clear();
					game.load_pgn(data.message[0])
					board.position(game.fen());
  		            BoardCharAddNewLine();
  		            break;
  		        case 1:
  		            // Warning / Advice messages
  		            ok_msg = data.message
  		            break;
  		        case 2:
  		            // Alert / Danger messages
  		            ok_msg = data.message
  		            break;
  		        case 3:
  		            // "Muted" messages
  		            ok_msg = data.message
  		            break;
  		        case 4:
  		            // User joined room
  		            ok_msg = data.username +
  		                    " joined the room!"
  		            socket.send(JSON.stringify({
					    "command": "PGN",
			            "room": chtor.roundId,
					}));
  		            break;
  		        case 5:
  		            // User left room
  		            console.log(data.username +" left the room!")
  		    		chtor.oppUserCheckConn = 0;
					//$('.connect_users').show();
  		    		$('.player_info[userId='+data.uid+'] .player_status').removeClass('active');
  		    		//$('.connect_users .block span').text('Connecting').removeClass('active');
  		            break;
  		        case 6:
  		        	if(parseInt(data.message)==0) {
  		        		$('.connect_users .block span').text('Connected').addClass('active');
						game_over_paused = false

  		        	}
  		            // User left room
  		           	$('.connect_users button').text('Start at: '+(chtor.startTimer - parseInt(data.message)))
  		           	if(chtor.startTimer - parseInt(data.message)<=0) {
  		           		game_over_paused = false;
						$('.connect_users').hide();
  		           	}
  		            break;
  		        case 7:
  		            if(data.username == chtor.users[0]) {

  		            } else {

  		            }
  		            break;
  		        case 8:
  		        	game.clear();
					board.position(game.fen());
					$('.connect_users').show();
					$('.connect_users .block').html('<p>Game is Over, You ' + (data.message==chtor.curUserId?'Win':'Lose') + '</p>');
  		        	break;
  		    }
  		} else {
  		    console.log("Cannot handle message!");
  		}
    };

    function timerToString(ms) {
    	var sec = parseInt(Math.ceil(ms/100%60));
    	var min = ms/100/60;
    	return parseInt(sec==60?Math.ceil(min):min).zeroPad(10)+":"+(sec==60?0:sec).zeroPad(10);
    }

    function BoardCharAddNewLine(is_over) {

		var status = '',winner = 0;
		var moveColor = 'White';
		if (game.turn() === 'b') {
			moveColor = 'Black';
		}
		// checkmate?
		if (game.in_checkmate() === true) {
			status = 'Game over, ' + moveColor + ' is in checkmate.';
		}
		// draw?
		else if (game.in_draw() === true) {
			status = 'Game over, drawn position';
		} 
		else if(is_over != undefined && is_over) {
			status = 'Game over, ' + moveColor + ' is time out.';
			game_over_paused = true;
		}

		if(moveColor == (chtor.white?'Black':'White'))
			winner = chtor.curUserId
		else
			winner = chtor.oppUserId

		if(status.length) {
			socket.send(JSON.stringify({
				    "command": "game_over",
		            "room": chtor.roundId,
		            "winner": winner
				}));
		}

		// timer
		var current_obj_time = $('.player_info.'+(game.turn()==='w'?'b':'w')).find('.timer').attr('timer');
		var spent_time;
		spent_time = [parseInt(spent_time/100/60),parseInt(spent_time/100%60),parseInt(spent_time%1000/10).zeroPad(10)];
		spent_time = isNaN(spent_time[2])?'':(spent_time[0]?spent_time[0]*60:0)+spent_time[1]+':'+spent_time[2]+'s';


		// add new line
		var str = game.pgn(),
			DOMpgnList = $('.chtor_step'),
			DOMhchBlock = $('.history_chat');

		if(str.length < 1) {
			DOMhchBlock.html('');
		}

		var _match = str.match(/\d+\.\s\w+[\+]?\s?(\w+[\+]?)?/g)
		if(_match != null) {
			var pgnList = [];
			for(i=0;i < _match.length;i++) {
				var b = /(\d+)\.\s(\w+[\+]?)\s?(\w+[\+]?)?/g.exec(_match[i]);
				pgnList.push(b)
			}
		
			for(i = 0; i < pgnList.length; i++) {
				if(DOMpgnList.eq(i).length != 0 && DOMpgnList.eq(i).attr('context') != pgnList[i][0]) {
					DOMpgnList.eq(i).attr('context', pgnList[i][0]);
					DOMpgnList.eq(i).find('.num').text(pgnList[i][1]).end().find('.white * li:eq(0)').text(pgnList[i][2]||"...").end().find('.black * li:eq(0)').text(pgnList[i][3]||"...");
				} else if(DOMpgnList.eq(i).length == 0) {
					var data_ = '';
					DOMhchBlock.append('<div class="chtor_step" context="' + pgnList[i][0] + '"><span class="num">' + pgnList[i][1] + '</span><span class="white"><ul><li>' + (pgnList[i][2]||"...") + '</li><li></li></ul></span><span class="black"><ul><li>' + (pgnList[i][3]||"...") + '</li><li></li></ul></span></div>');
				}
			}
		}
		DOMhchBlock.animate({ scrollTop: DOMhchBlock[0].scrollHeight}, 250).append(status.length && $('.g_over').length == 0?'<div class="chtor_step g_over"><span class="text">'+status+'</span></div>':'');


		// get list of captured figures
		var history = game.history({verbose: true});
		var captured = history.reduce(function(acc, move) {
			if ('captured' in move) {
				var piece = move.captured;
				var color = move.color == 'w' ? 'b' : 'w';
				acc[color].push(piece);
				return acc;
			} else {
				return acc;
			}
		}, {w: [], b: []});

		for(color in captured) {
			if(captured[color].length) {
				var color_obj = cap_trach.filter('.'+color),
					obj_cap_length = color_obj.attr('cap_string').length,
					dt_cap_length = captured[color].length;

				if(obj_cap_length>captured[color].length)
					color_obj.attr('cap_string','');

				var string_diff = dt_cap_length - (dt_cap_length-obj_cap_length);

				for(i = string_diff; i < dt_cap_length; i++){
					color_obj.attr('cap_string',captured[color].join('')).append('<img class="captured_chess" src="/static/img/chesspieces/wikipedia/' + color +captured[color][i].toUpperCase()+'.png" >');
				}
			}
		}
	}


	// do not pick up pieces if the game is over
	// only pick up pieces for the side to move
	var onDragStart = function(source, piece, position, orientation) {
		if(game_over_paused)
			return false;
		if (game.game_over() === true ||
			(game.turn() !== (chtor.white?'w':'b')) ||
		    (game.turn() === 'w' && piece.search(/^b/) !== -1) ||
		    (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
			return false;
		}
	};

	var onDrop = function(source, target) {
		// see if the move is legal
		var move = game.move({
		  from: source,
		  to: target,
		  promotion: 'q' // NOTE: always promote to a queen for example simplicity
		});

		socket.send(JSON.stringify({
		    "command": "make_move",
		    "room": chtor.roundId,
		    "pgn": game.pgn(),
		    "turn": game.turn()
		}));

		// illegal move
		if (move === null) return 'snapback';

		BoardCharAddNewLine()
	};

	// update the board position after the piece snap 
	// for castling, en passant, pawn promotion
	var onSnapEnd = function() {
	  board.position(game.fen());
	};

var cfg = {
	draggable: true,
	onDragStart: onDragStart,
	onDrop: onDrop,
	onSnapEnd: onSnapEnd,
	moveSpeed: 'slow',
  	snapbackSpeed: 500,
  	snapSpeed: 100,
};
board = ChessBoard('chboard', cfg);

game_timers = setInterval(function(){
	if(!game_over_paused) {
		var timer_obj = $('.player_info.'+game.turn()).find('.timer');
		var new_time = parseInt(timer_obj.attr('timer')) - 10;
		if(new_time <= 0) {
			BoardCharAddNewLine(true);
			clearInterval(game_timers)
		}
		timer_obj.attr('timer',new_time);
		var time_left = timer_obj.attr('timer');
		timer_obj.text(timerToString(time_left))
	}
},100)

BoardCharAddNewLine();
})


Number.prototype.zeroPad = Number.prototype.zeroPad || function(base){
	var nr = this, len = (String(base).length - String(nr).length)+1;
	return len > 0? new Array(len).join('0')+nr : nr;
};