'use strict';

app.factory('SourceQueue', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS) {
        var last_error = "";
        var events = [];

        function queue_event(msg) {
            if (msg['error'] == 0) {
                this.events = msg['data'];
            } else {
                last_error = msg['data']['message'];
            }
        }

        function setup() {
            SockService.add_recv_handler('queue', queue_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                fetchAll();
            });
        }

        function fetchAll() {
            SockService.send({
                'type': 'queue',
                'message': {
                    'query': 'fetchall'
                }
            });
        }

        function get_events() {
            return [];
        }

        function get_queues(event_id) {
            return [];
        }

        function add(queue_id, url) {

        }

        function remove(queue_id, remove) {

        }

        function get_queue_unplayed(queue_id) {
            return [];
        }

        function get_queue_all(queue_id) {
            return [];
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            add: add,
            remove: remove,
            get_events: get_events,
            get_queues: get_queues,
            get_queue_unplayed: get_queue_unplayed,
            get_queue_all: get_queue_all,
            get_last_error: get_last_error
        };
    }
]);
