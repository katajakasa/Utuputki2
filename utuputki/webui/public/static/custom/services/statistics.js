'use strict';

app.factory('Statistics', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var most_received = [];
        var most_given = [];

        function stats_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == 'fetch_most_received') {
                    most_received = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.statsRefresh);
                    return;
                }
                if(query == 'fetch_most_given') {
                    most_given = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.statsRefresh);
                    return;
                }
                console.error("Unknown incoming stats packet subtype!")
            }
        }

        function setup() {
            SockService.add_recv_handler('stats', stats_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                refresh();
            });
        }

        function get_most_given() {
            return most_given;
        }

        function get_most_received() {
            return most_received;
        }

        function get_last_error() {
            return last_error;
        }

        function refresh() {
            SockService.send_msg('stats', {}, 'fetch_most_received');
            SockService.send_msg('stats', {}, 'fetch_most_given');
        }

        return {
            setup: setup,
            get_last_error: get_last_error,
            get_most_given: get_most_given,
            get_most_received: get_most_received,
            refresh: refresh
        };
    }
]);
