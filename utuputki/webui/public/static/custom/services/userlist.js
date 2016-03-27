'use strict';

app.factory('UserList', ['$location', '$rootScope', 'SockService', 'AuthService', 'AUTH_EVENTS', 'SYNC_EVENTS', 'USERLEVELS',
    function ($location, $rootScope, SockService, AuthService, AUTH_EVENTS, SYNC_EVENTS, USERLEVELS) {
        var last_error = "";
        var users = [];

        function event_userlist(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == "fetchall") {
                    users = msg['data'];
                }
                if(query == "edit") {
                    for(var i = 0; i < users.length; i++) {
                        if(users[i].id == msg['data']['id']) {
                            users[i].email = msg['data']['email'];
                            users[i].alias = msg['data']['alias'];
                        }
                    }
                }
            }
        }

        function edit_user(id, nickname, email) {
            SockService.send_msg('userlist', {
                'id': id,
                'nickname': nickname,
                'email': email
            }, 'edit');
            console.log(id);
        }

        function setup() {
            SockService.add_recv_handler('userlist', event_userlist);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                if(AuthService.is_authorized(USERLEVELS['admin'])) {
                    SockService.send_msg('userlist', {}, 'fetchall');
                }
            });
        }

        function get_users() {
            return users;
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            edit_user: edit_user,
            get_users: get_users,
            get_last_error: get_last_error
        };
    }
]);
