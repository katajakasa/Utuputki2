'use strict';

app.factory('Event', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var events = [];

        function event_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                events = msg['data'];
                $rootScope.$broadcast(SYNC_EVENTS.eventsRefresh);
            }
        }

        function setup() {
            SockService.add_recv_handler('event', event_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send_msg('event', {}, 'fetchall');
            });
        }

        function get_events() {
            return events;
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            get_events: get_events,
            get_last_error: get_last_error
        };
    }
]);
