'use strict';

app.factory('AuthService', ['$location', '$rootScope', 'Session', 'User', 'AUTH_EVENTS', 'SockService',
    function ($location, $rootScope, Session, User, AUTH_EVENTS, SockService) {
        var last_error = "";

        function auth_event(msg, query) {
            if(msg['error'] == 1) {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.sessionTimeout);
                console.error("Session timeout!");
            } else {
                Session.create(
                    msg['data']['sid'],
                    msg['data']['uid'],
                    msg['data']['user']['level']
                );
                User.create(msg['data']['user']);
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
            }
        }

        function authenticate() {
            SockService.send_msg('auth', {
                'sid': Session.sid
            });
        }

        function login_event(msg, query) {
            if(msg['error'] == 1) {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
            } else {
                Session.create(
                    msg['data']['sid'],
                    msg['data']['uid'],
                    msg['data']['user']['level']
                );
                User.create(msg['data']['user']);
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
            }
        }

        function register_event(msg, query) {
            if(msg['error'] == 1) {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.registerFailed);
            } else {
                $rootScope.$broadcast(AUTH_EVENTS.registerSuccess);
            }
        }

        function profile_event(msg, query) {
            if(msg['error'] == 1) {
                last_error = msg['data']['message'];
                $rootScope.$broadcast(AUTH_EVENTS.profileFailed);
            } else {
                User.update(msg['data']['user']);
                $rootScope.$broadcast(AUTH_EVENTS.profileSuccess);
            }
        }

        function login(credentials) {
            SockService.send_msg('login', {
                'username': credentials.username,
                'password': credentials.password
            });
        }

        function update_profile(profile) {
            SockService.send_msg('profile', {
                'password': profile.password,
                'password2': profile.password2,
                'nickname': profile.nickname,
                'email': profile.email
            });
        }

        function register(new_user) {
            SockService.send_msg('register', {
                'username': new_user.username,
                'password': new_user.password,
                'password2': new_user.password2,
                'nickname': new_user.nickname,
                'email': new_user.email
            });
        }

        function logout() {
            $rootScope.$broadcast(AUTH_EVENTS.logoutBegin);
            SockService.send_msg('logout', {});
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
            SockService.add_recv_handler('profile', profile_event);
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            authenticate: authenticate,
            login: login,
            logout: logout,
            update_profile: update_profile,
            is_authorized: is_authorized,
            is_authenticated: is_authenticated,
            get_last_error: get_last_error,
            session_id: session_id,
            register: register
        };
    }
]);
