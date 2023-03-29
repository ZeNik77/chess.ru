var board = null
var game = new Chess()
var $status = $('#status')
// var $debug = $('#debug')
var socket = new WebSocket('ws://' + location.host + '/gamesock');
var urlParams = new URLSearchParams(window.location.search);
var id = urlParams.get('id')
var pos = 'start';

socket.onopen = function (e) {
    console.log("[open] Connection established");
    socket.send(id)
};

socket.onmessage = function (event) {
    console.log(`[message] Data received from server: ${event.data}`);
    pos = event.data
    game.load(event.data)
    board.position(event.data)
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
    if (game.game_over()) return false

    // only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
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
        socket.send('checkmate');
    }

    // draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position'
        socket.send('draw');

    }

    // game still on
    else {
        status = moveColor + ' to move'

        // check?
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check'
        }
        socket.send(game.fen());
    }
    $status.text(status)


}

var config = {
    draggable: true,
    position: pos,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}
board = Chessboard('myBoard', config)

updateStatus()
