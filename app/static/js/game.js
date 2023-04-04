var board = null
var game = new Chess()
var $status = $('#status')
// var $debug = $('#debug')
var socket = new WebSocket('ws://' + location.host + '/gamesock');
var urlParams = new URLSearchParams(window.location.search);
var id = urlParams.get('id')
var pos = 'start';
var orient = 'white';
var state = 'lobby';
socket.onopen = function (e) {
    console.log("[open] Connection established");
    var pack = {type: 'JOIN', roomid: id};
    pack = JSON.stringify(pack)
    socket.send(pack)
};

socket.onmessage = function (event) {
    console.log(`[message] Data received from server: ${event.data}`);
    if (event.data == 'OK') {
        var pack = {type: 'GET', roomid: id};
        pack = JSON.stringify(pack)
        socket.send(pack)
    } else {
        var dt = JSON.parse(event.data.replace(/'/g, '"'))
        if (dt.type == 'GET') {
            pos = dt.fen
            game.load(dt.fen)
            board.position(dt.fen)
            console.log(orient)
            if (dt.orientation != orient) {
                orient = dt.orientation
                board.flip()
            }
            if (!dt.lobby) {
                state = 'game';
            }
            updateStatus()
        }
    }
};

socket.onclose = function (event) {
    if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        console.log('[close] Connection died');
    }
};

socket.onerror = function (error) {
    console.log(error);
};

function onDragStart(source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over() || state != 'game') return false

    // only pick up pieces for the side to move
    if ((orient === 'white' && piece.search(/^b/) !== -1) ||
        (orient === 'black' && piece.search(/^w/) !== -1)) {
        return false
    }
}

function onDrop(source, target) {
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })

    // illegal move
    if (move === null) return 'snapback'

    updateStatus()
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd() {
    board.position(game.fen())
}

function updateStatus() {
    var status = ''

    var moveColor = 'White'
    if (game.turn() === 'b') {
        moveColor = 'Black'
    }

    // checkmate?
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.'
        var pack = {type: 'END', roomid: id, wintype: 'win', winner: game.turn()};
        pack = JSON.stringify(pack)
        socket.send(pack);
        state = 'end'
        $status.text('WIN ' + game.turn())
    }

    // draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position'
        var pack = {type: 'END', roomid: id, wintype: 'draw'};
        pack = JSON.stringify(pack)
        socket.send(pack);
        state = 'end'
        $status.text('DRAW')


    }

    // game still on
    else {
        status = moveColor + ' to move'

        // check?
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check'
        }
        var pack = {type: 'UPDATE', roomid: id, fen: game.fen()};
        pack = JSON.stringify(pack)
        socket.send(pack);
    }
    console.log(state)
    if (state == 'game') {
        $status.text(status)
    } else {
        $status.text('Lobby mode')
    }


}

var config = {
    draggable: true,
    position: pos,
    orientation: orient,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)
updateStatus()
