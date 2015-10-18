'use strict';

app.factory('AuthService', ['$location', '$rootScope', 'Session', 'User', 'AUTH_EVENTS', 'SockService',
    function ($location, $rootScope, Session, User, AUTH_EVENTS, SockService) {
        var last_error = "";

        function auth_event(msg) {
            if (msg['error'] == 0) {
                Session.create(
                    msg['data']['sid'],
                    msg['data']['uid'],
                    msg['data']['user']['level']
                );
                User.create(msg['data']['user']);
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                console.log("Authentication success!");
            } else {
                $rootScope.$broadcast(AUTH_EVENTS.sessionTimeout);
                console.error("Session timeout!");
            }
        }

        function authenticate() {
            SockService.send({
                'type': 'auth',
                'message': {
                    'sid': Session.sid
                }
            });
        }

        function login_event(msg) {
            if (msg['error'] == 0) {
                Session.create(
                    msg['data']['sid'],
                    msg['data']['uid'],
                    msg['data']['user']['level']
                );
                User.create(msg['data']['user']);
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
            } else {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
            }
        }

        function register_event(msg) {
            if (msg['error'] == 0) {
                $rootScope.$broadcast(AUTH_EVENTS.registerSuccess);
            } else {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.registerFailed);
            }
        }

        function login(credentials) {
            SockService.send({
                'type': 'login',
                'message': {
                    'username': credentials.username,
                    'password': credentials.password
                }
            });
        }

        function register(new_user) {
            SockService.send({
                'type': 'register',
                'message': {
                    'username': new_user.username,
                    'password': new_user.password,
                    'nickname': new_user.nickname,
                    'email': new_user.email
                }
            });
        }

        function logout() {
            $rootScope.$broadcast(AUTH_EVENTS.logoutBegin);
            SockService.send({
                'type': 'logout',
                'message': {}
            });
            Session.destroy();
            User.destroy();
            $rootScope.$broadcast(AUTH_EVENTS.logoutSuccess);
        }

        function is_authenticated() {
            return !!Session.uid;
        }

        function session_id() {
            return Session.sid;
        }

        function is_authorized(req_level) {
            return (is_authenticated() && req_level >= Session.level);
        }

        function setup() {
            SockService.add_recv_handler('auth', auth_event);
            SockService.add_recv_handler('login', login_event);
            SockService.add_recv_handler('register', register_event);
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            authenticate: authenticate,
            login: login,
            logout: logout,
            is_authorized: is_authorized,
            is_authenticated: is_authenticated,
            get_last_error: get_last_error,
            session_id: session_id
        };
    }
]);
