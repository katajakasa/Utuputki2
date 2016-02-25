'use strict';

app.controller('NavController', ['$scope', '$rootScope', '$location', 'AuthService', 'Event', 'Player', 'Session', 'SYNC_EVENTS', 'AUTH_EVENTS', 'USERLEVELS',
    function ($scope, $rootScope, $location, AuthService, Event, Player, Session, SYNC_EVENTS, AUTH_EVENTS, USERLEVELS) {
        $scope.events = [];
        $scope.players = [];
        $scope.c_event = null;
        $scope.c_player = null;

        $scope.sites = [
            {url: '/', name: 'My Queue', requireLogin: true},
            {url: '/playlist', name: 'Playlist', requireLogin: true},
            {url: '/history', name: 'History', requireLogin: true},
            {url: '/stats', name: 'Statistics', requireLogin: true},
            {url: '/profile', name: 'Profile', requireLogin: true},
            {url: '/login', name: 'Login', requireLogin: false},
            {url: '/register', name: 'Register', requireLogin: false},
            {url: '/logout', name: 'Logout', requireLogin: true}
        ];

        $scope.is_site_active = function (loc) {
            return (loc === $location.path());
        };

        $scope.is_site_visible = function (url) {
            for (var i = 0; i < $scope.sites.length; i++) {
                if ($scope.sites[i].url == url) {
                    if ($scope.sites[i].requireLogin) {
                        return (AuthService.is_authenticated());
                    } else {
                        return (!AuthService.is_authenticated());
                    }
                }
            }
            return true;
        };

        $scope.is_event_menu_visible = function() {
            return (AuthService.is_authenticated());
        };

        $scope.is_admin = function() {
            return Session.hasLevel(USERLEVELS['admin']);
        };

        function refresh_events() {
            $scope.events = Event.get_visible_events();
            if($scope.events.length > 0 && Event.get_selected_event() == null) {
                $scope.c_event = $scope.events[$scope.events.length - 1];
                Event.set_selected_event($scope.c_event.id);
                refresh_players();
            }
        }

        function refresh_players() {
            if($scope.c_event == null) {
                $scope.c_player = null;
                return;
            }
            $scope.players = Player.get_players($scope.c_event.id);
            if($scope.players.length > 0) {
                $scope.c_player = $scope.players[$scope.players.length-1];
            } else {
                $scope.c_player = null;
            }
        }

        $scope.on_event_change = function(event) {
            if($scope.c_event.id != event.id) {
                $scope.c_event = event;
                Event.set_selected_event(event.id);
                refresh_players();
            }
        };

        $scope.on_player_change = function(player) {
            if($scope.c_player.id != player.id) {
                $scope.c_player = player;
                Player.set_current_player(player);
            }
        };

        function init() {
            refresh_events();
            refresh_players();

            $rootScope.$on(SYNC_EVENTS.eventsRefresh, function(event, args) {
                refresh_events();
            });
            $rootScope.$on(SYNC_EVENTS.playersRefresh, function(event, args) {
                refresh_players();
            });
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                refresh_events();
                refresh_players();
            });
        }

        init();
    }
]);
