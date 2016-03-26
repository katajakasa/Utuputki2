'use strict';

app.factory('Player', ['$location', '$rootScope', 'SockService', 'Playlist', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, Playlist, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var players = [];
        var current_player = null;
        var req_skip_count = 1;
        var media_skip_count = 0;

        function player_event(msg, query) {
            if(msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == 'fetchall') {
                    players = msg['data'];
                    localStorage.setItem("players_list", JSON.stringify(players));
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                    if(current_player == null && players.length > 0) {
                        current_player = players[0];
                        $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
                    }
                    return;
                }
                if(query == 'add') {
                    players.push(msg['data']);
                    localStorage.setItem("players_list", JSON.stringify(players));
                    $rootScope.$broadcast(SYNC_EVENTS.playerAdded);
                    return;
                }
                if(query == "edit") {
                    for(var k = 0; k < players.length; k++) {
                        if(players[k].id == msg['data']['id']) {
                            players[k].name = msg['data']['name'];
                        }
                    }
                    localStorage.setItem("players_list", JSON.stringify(players));
                    $rootScope.$broadcast(SYNC_EVENTS.playersEdited);
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                    return;
                }
                if(query == 'change') {
                    for(var i = 0; i < players.length; i++) {
                        if(players[i].id == msg['data']['state']['id']) {
                            players[i] = msg['data']['state'];
                            if(current_player != null && current_player.id == players[i].id) {
                                current_player = players[i];
                            }
                        }
                    }
                    $rootScope.$broadcast(SYNC_EVENTS.playerPlaybackChange);
                    return;
                }
                if(query == 'req_skip_count') {
                    req_skip_count = msg['data']['count'];
                    $rootScope.$broadcast(SYNC_EVENTS.playerSkipCountChange);
                    return;
                }
                if(query == 'current_skip_count') {
                    media_skip_count = msg['data']['count'];
                    $rootScope.$broadcast(SYNC_EVENTS.playerSkipCountChange);
                    return;
                }
                console.error("Unidentified query type.");
            }
        }

        function setup() {
            SockService.add_recv_handler('player', player_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                // If cache contains old players list & current player, fetch them
                if(localStorage.getItem("players_list") !== null) {
                    players = JSON.parse(localStorage.getItem("players_list"));
                    current_player = JSON.parse(localStorage.getItem("selected_player"));
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                }

                // ... then ask for a refresh from server
                SockService.send_msg('player', {}, 'fetchall');
                SockService.send_msg('player', {}, 'req_skip_count');
                var c_player = get_current_player();
                if(c_player != null) {
                    SockService.send_msg('player', {'player_id': c_player.id}, 'now_playing');
                    SockService.send_msg('player', {'player_id': c_player.id}, 'get_media_skip_count');
                }
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

        function add_player(event_id) {
            SockService.send_msg('player', {
                event_id: event_id
            }, 'add');
        }

        function edit_player(id, name) {
            SockService.send_msg('player', {
                'id': id,
                'name': name
            }, 'edit');
        }

        function get_current_player() {
            return current_player;
        }

        function get_current_media() {
            var c_player = get_current_player();
            if(c_player != null) {
                return Playlist.get_media(c_player.last);
            }
            return null;
        }

        function get_current_status() {
            var c_player = get_current_player();
            if(c_player != null) {
                return c_player.status;
            }
            return 0;
        }

        function skip_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'skip');
            }
        }

        function forceskip_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'force_skip');
            }
        }

        function stop_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'stop');
            }
        }

        function play_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'play');
            }
        }

        function pause_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'pause');
            }
        }

        function set_current_player(player) {
            localStorage.setItem("selected_player", JSON.stringify(player));
            current_player = player;
            $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
        }

        function get_req_skip_count() {
            return req_skip_count;
        }

        function get_current_skip_count() {
            return media_skip_count;
        }

        function get_last_error() {
            return last_error;
        }

        function refresh() {
            SockService.send_msg('player', {}, 'req_skip_count');
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'now_playing');
                SockService.send_msg('player', {'player_id': c_player.id}, 'get_media_skip_count');
            }
        }

        return {
            setup: setup,
            get_players: get_players,
            get_last_error: get_last_error,
            get_current_player: get_current_player,
            set_current_player: set_current_player,
            get_req_skip_count: get_req_skip_count,
            get_current_media: get_current_media,
            get_current_status: get_current_status,
            get_current_skip_count: get_current_skip_count,
            skip_current: skip_current,
            refresh: refresh,
            add_player: add_player,
            edit_player: edit_player,
            forceskip_current: forceskip_current,
            stop_current: stop_current,
            play_current: play_current,
            pause_current: pause_current
        };
    }
]);
