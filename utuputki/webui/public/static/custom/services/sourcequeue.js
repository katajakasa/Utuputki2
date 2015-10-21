'use strict';

app.factory('SourceQueue', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var queues = [];

        function update_status(source_id, status) {
            for(var i = 0; i < queues.length; i++) {
                for(var k = 0; k < queues[i].items[0].length; k++) {
                    if(queues[i].items[0][k].source[0].id == source_id) {
                        queues[i].items[0][k].source[0].status = status;
                    }
                }
            }
        }

        function update_single_data(data) {
            for(var i = 0; i < queues.length; i++) {
                for(var k = 0; k < queues[i].items[0].length; k++) {
                    if(queues[i].items[0][k].source[0].id == data.id) {
                        queues[i].items[0][k].source[0] = data;
                    }
                }
            }
        }

        function queue_event(msg) {
            if (msg['error'] == 0) {
                if(msg['query'] == 'fetchall') {
                    queues = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.queuesRefresh);
                    return;
                }
                if(msg['query'] == 'add') {
                    $rootScope.$broadcast(SYNC_EVENTS.queueAddSuccess);
                    return;
                }
                if(msg['query'] == 'status') {
                    console.log(msg['data']);
                    update_status(msg['data']['source_id'], msg['data']['status']);
                    $rootScope.$broadcast(SYNC_EVENTS.queuesRefresh);
                    return;
                }
                if(msg['query'] == 'single') {
                    console.log(msg['data']);
                    update_single_data(msg['data']);
                    $rootScope.$broadcast(SYNC_EVENTS.queuesRefresh);
                    return;
                }
                console.error("Unknown incoming queue packet subtype!")
            } else {
                last_error = msg['data']['message'];
                if(msg['query'] == 'add') {
                    $rootScope.$broadcast(SYNC_EVENTS.queueAddFailed);
                }
            }
        }

        function setup() {
            SockService.add_recv_handler('queue', queue_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send({
                    'type': 'queue',
                    'message': {
                        'query': 'fetchall'
                    }
                });
            });
        }

        function get_queue_num(player_id) {
            for(var i = 0; i < queues.length; i++) {
                if(queues[i].target == player_id) {
                    return i;
                }
            }
            return -1;
        }

        function get_queue(queue_num) {
            return queues[queue_num];
        }

        function add(player_id, url) {
            SockService.send({
                'type': 'queue',
                'message': {
                    'query': 'add',
                    'player_id': player_id,
                    'url': url
                }
            });
        }

        function remove(queue_id, remove) {

        }

        function get_last_error() {
            return last_error;
        }

        return {
            queues: queues,
            setup: setup,
            add: add,
            remove: remove,
            get_queue_num: get_queue_num,
            get_queue: get_queue,
            get_last_error: get_last_error
        };
    }
]);
