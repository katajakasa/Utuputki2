'use strict';

app.factory('Player', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var players = [];
        var current_player = null;

        function player_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == 'fetchall') {
                    players = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                    if(current_player == null && players.length > 0) {
                        current_player = players[0];
                        $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
                    }
                }
                if(query == 'change') {
                    for(var i = 0; i < players.length; i++) {
                        if(players[i].id == msg['player_id']) {
                            players[i].last = msg['last_id'];
                        }
                    }
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                }

            }
        }

        function setup() {
            SockService.add_recv_handler('player', player_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send_msg('player', {}, 'fetchall');
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

        function get_current_player() {
            return current_player;
        }

        function set_current_player(player) {
            current_player = player;
            $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            get_players: get_players,
            get_last_error: get_last_error,
            get_current_player: get_current_player,
            set_current_player: set_current_player
        };
    }
]);
