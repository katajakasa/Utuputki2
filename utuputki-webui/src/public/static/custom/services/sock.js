'use strict';

app.factory('SockService', ['socket',
    function (socket) {
        var recv_handlers = {};
        var open_handlers = [];

        function setup() {
            socket.onOpen(function () {
                for (var i = 0; i < open_handlers.length; i++) {
                    open_handlers[i]();
                }
            });
            socket.onMessage(function (msg) {
                var type = msg['type'];
                if (type in recv_handlers) {
                    for (var i = 0; i < recv_handlers[type].length; i++) {
                        recv_handlers[type][i](msg);
                    }
                }
            });
        }

        function add_open_handler(fn) {
            open_handlers.push(fn);
        }

        function add_recv_handler(type, fn) {
            recv_handlers[type] = [];
            recv_handlers[type].push(fn);
        }

        function send(msg) {
            socket.send(msg)
        }

        return {
            setup: setup,
            add_open_handler: add_open_handler,
            add_recv_handler: add_recv_handler,
            send: send
        }
    }
]);
