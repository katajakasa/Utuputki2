'use strict';

app.factory('Player', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS) {
        var last_error = "";
        var players = [];

        function player_event(msg) {
            if (msg['error'] == 0) {
                players = msg['data'];
            } else {
                last_error = msg['data']['message'];
            }
        }

        function setup() {
            SockService.add_recv_handler('player', player_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send({
                    'type': 'player',
                    'message': {
                        'query': 'fetchall'
                    }
                });
            });
        }

        function get_players(event_id) {
            var out = [];
            for(var i = 0; i < players.length; i++) {
                if(players[i].event_id == event_id) {
                    out.push(players[i]);
                }
            }
            return out;
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            get_players: get_players,
            get_last_error: get_last_error
        };
    }
]);
