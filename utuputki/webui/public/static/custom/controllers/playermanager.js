'use strict';

app.controller('PlayerManagerController', ['$scope', '$rootScope', '$location', 'AuthService', 'Event', 'Player', 'Session', 'SYNC_EVENTS', 'AUTH_EVENTS', 'USERLEVELS',
    function ($scope, $rootScope, $location, AuthService, Event, Player, Session, SYNC_EVENTS, AUTH_EVENTS, USERLEVELS) {
        $scope.req_skip_count = 1;
        $scope.current_skip_count = 0;
        $scope.now_playing = "-";
        $scope.status = "Stopped";
        $scope.skip_enabled = false;

        var statuslist = [
            'Stopped',
            'Playing',
            'Paused'
        ];

        function init() {
            $rootScope.$on(SYNC_EVENTS.playerSkipCountChange, function (event, args) {
                $scope.req_skip_count = Player.get_req_skip_count();
                $scope.current_skip_count = Player.get_current_skip_count();
            });
            $rootScope.$on(SYNC_EVENTS.playerPlaybackChange, function (event, args) {
                $scope.now_playing = Player.get_current_media().source.title;
                $scope.current_skip_count = 0;
                var st = Player.get_current_status();
                if(st != null) {
                    if(st == 0) {
                        $scope.now_playing = '-';
                    }
                    $scope.status = statuslist[st];
                    $scope.skip_enabled = (st != 0);
                } else {
                    $scope.now_playing = '-';
                }
            });
            Player.refresh();
        }

        $scope.on_skip_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 0) {
                Player.skip_current();
            }
        };

        $scope.is_admin = function() {
            return Session.hasLevel(USERLEVELS['admin']);
        };

        init();
    }
]);
