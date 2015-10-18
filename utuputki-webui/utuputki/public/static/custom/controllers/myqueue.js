'use strict';

app.controller('MyQueueController', ['$scope', '$location', 'Player', 'Event', 'SourceQueue',
    function ($scope, $location, Player, Event, SourceQueue) {
        $scope.events = [];
        $scope.players = [];
        $scope.queue = [];
        $scope.c_event = null;
        $scope.c_player = null;

        function refresh_events() {
            $scope.events = Event.get_events();
            $scope.c_event = $scope.events[$scope.events.length-1];
        }

        function refresh_players() {
            $scope.players = Player.get_players($scope.c_event.id);
            $scope.c_player = $scope.players[$scope.players.length-1];
        }

        function refresh_queue() {
            var num = SourceQueue.get_queue_num($scope.c_event.id, $scope.c_player.id);
            $scope.queue = SourceQueue.get_queue_items(num);
        }

        function init() {
            refresh_events();
            refresh_players();
            refresh_queue();
        }

        $scope.sel_event = function(event) {
            $scope.c_event = event;
            refresh_players();
            refresh_queue();
        };

        $scope.sel_player = function(player) {
            $scope.c_player = player;
            refresh_queue();
        };

        init();
    }
]);
