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
            for(var i = 0; i < $scope.sites.length; i++) {
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
            /**
             * Checks if the event menu should be visible
             * @return {boolean} Is the event menu visible
             */
            return (AuthService.is_authenticated());
        };

        $scope.is_admin = function() {
            /**
             * Checks if user is Administrator by userlevel
             * @return {boolean} Is user admin
             */
            return Session.hasLevel(USERLEVELS['admin']);
        };

        function refresh_events() {
            /**
             * Refresh the contents of the events navigation list
             */
            $scope.events = Event.get_visible_events();
            if($scope.events.length > 0) {
                $scope.c_event = Event.get_selected_event();
                if($scope.c_event === null) {
                    $scope.c_event = $scope.events[$scope.events.length - 1];
                    Event.set_selected_event($scope.c_event);
                }
                refresh_players();
            }
        }

        function refresh_players() {
            /**
             * Refresh the contents of the players navigation list
             */
            if($scope.c_event == null) {
                $scope.c_player = null;
                return;
            }
            $scope.players = Player.get_players($scope.c_event.id);
            if($scope.players.length > 0) {
                $scope.c_player = Player.get_current_player();
                if($scope.c_player == null || $scope.c_player.event_id != $scope.c_event.id) {
                    $scope.c_player = $scope.players[0];
                    Player.set_current_player($scope.c_player);
                }
            } else {
                $scope.c_player = null;
            }
        }

        $scope.on_event_change = function(event) {
            /**
             * Handles Navigation event changes
             *
             * @param {Event] player - Event object to change to
             */
            if($scope.c_event == null || $scope.c_event.id != event.id) {
                $scope.c_event = event;
                Event.set_selected_event(event);
                refresh_players();
                Player.set_current_player($scope.c_player);
            }
        };

        $scope.on_player_change = function(player) {
            /**
             * Handles Navigation player changes
             *
             * @param {Player] player - Player object to change to
             */
            if($scope.c_player == null || $scope.c_player.id != player.id) {
                $scope.c_player = player;
                Player.set_current_player(player);
            }
        };

        function init() {
            /**
             * Initializes event listeners for the navigation menu
             */
            $rootScope.$on(SYNC_EVENTS.eventsRefresh, function(event, args) {
                refresh_events();
            });
            $rootScope.$on(SYNC_EVENTS.playersRefresh, function(event, args) {
                refresh_events();
                refresh_players();
            });
        }

        init();
    }
]);
