'use strict';

app.factory('Event', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var events = [];
        var selected_event = null;

        function event_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == "fetchall") {
                    events = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.eventsRefresh);
                }
                if(query == "add") {
                    events.push(msg['data']);
                    $rootScope.$broadcast(SYNC_EVENTS.eventAdded);
                    $rootScope.$broadcast(SYNC_EVENTS.eventsRefresh);
                }
                if(query == "edit") {
                    for(var i = 0; i < events.length; i++) {
                        if(events[i].id == msg['data']['id']) {
                            events[i].visible = msg['data']['visible'];
                            events[i].name = msg['data']['name'];
                        }
                    }
                    $rootScope.$broadcast(SYNC_EVENTS.eventsEdited);
                    $rootScope.$broadcast(SYNC_EVENTS.eventsRefresh);
                }
            }
        }

        function add_event() {
            SockService.send_msg('event', {}, 'add');
        }

        function edit_event(id, name, visible) {
            SockService.send_msg('event', {
                'id': id,
                'name': name,
                'visible': visible
            }, 'edit');
        }

        function setup() {
            SockService.add_recv_handler('event', event_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send_msg('event', {}, 'fetchall');
            });
        }

        function get_visible_events() {
            var ev_list = [];
            for(var i = 0; i < events.length; i++) {
                if(events[i].visible) {
                    ev_list.push(events[i]);
                }
            }
            return ev_list;
        }

        function set_selected_event(id) {
            selected_event = id;
        }

        function get_selected_event() {
            return selected_event;
        }

        function get_events() {
            return events;
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            get_visible_events: get_visible_events,
            add_event: add_event,
            set_selected_event: set_selected_event,
            get_selected_event: get_selected_event,
            edit_event: edit_event,
            get_events: get_events,
            get_last_error: get_last_error
        };
    }
]);
