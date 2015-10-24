'use strict';

app.controller('PlayerManagerController', ['$scope', '$rootScope', '$location', 'AuthService', 'Event', 'Player', 'Session', 'SYNC_EVENTS', 'AUTH_EVENTS', 'USERLEVELS',
    function ($scope, $rootScope, $location, AuthService, Event, Player, Session, SYNC_EVENTS, AUTH_EVENTS, USERLEVELS) {
        $scope.req_skip_count = 1;
        $scope.current_skip_count = 0;
        $scope.now_playing = "-";
        $scope.now_playing_duration = 0;
        $scope.status = "Stopped";
        $scope.skip_enabled = false;
        $scope.np_duration_enabled = false;

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
                var media = Player.get_current_media();
                if(media != null) {
                    $scope.now_playing = media.source.title;
                    $scope.now_playing_duration =  moment.duration(media.source.length_seconds, "seconds").format("mm:ss", { trim: false });
                }
                $scope.current_skip_count = 0;
                var st = Player.get_current_status();
                if(st != null) {
                    if(st == 0) {
                        $scope.now_playing = '-';
                        $scope.now_playing_duration = 0;
                    }
                    $scope.status = statuslist[st];
                    $scope.skip_enabled = (st != 0);
                } else {
                    $scope.now_playing = '-';
                    $scope.now_playing_duration = 0;
                }
                $scope.np_duration_enabled = ($scope.now_playing_duration != 0);
            });
            Player.refresh();
        }

        $scope.on_skip_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 0) {
                Player.skip_current();
            }
        };

        $scope.on_stop_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 0) {
                Player.stop_current();
            }
        };

        $scope.on_play_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 1) {
                Player.play_current();
            }
        };

        $scope.on_pause_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 0) {
                Player.pause_current();
            }
        };

        $scope.on_forceskip_current = function() {
            var st = Player.get_current_status();
            if(st != null && st != 0) {
                Player.forceskip_current();
            }
        };

        $scope.is_admin = function() {
            return Session.hasLevel(USERLEVELS['admin']);
        };

        init();
    }
]);
