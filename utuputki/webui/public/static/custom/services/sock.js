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
                var query = msg['query'];
                if (type in recv_handlers) {
                    for (var i = 0; i < recv_handlers[type].length; i++) {
                        recv_handlers[type][i](msg, query);
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

        function send_msg(type, msg, query) {
            var data = {
                'type': type,
                'data': msg
            };
            if(query != undefined) {
                data['query'] = query;
            }
            socket.send(data)
        }

        return {
            setup: setup,
            add_open_handler: add_open_handler,
            add_recv_handler: add_recv_handler,
            send_msg: send_msg
        }
    }
]);
