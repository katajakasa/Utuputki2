'use strict';

app.controller('MyQueueController', ['$scope', '$location', 'Player', 'Event', 'SourceQueue', 'SYNC_EVENTS',
    function ($scope, $location, Player, Event, SourceQueue, SYNC_EVENTS) {
        $scope.events = [];
        $scope.players = [];
        $scope.c_event = null;
        $scope.c_player = null;

        $scope.grid_opts = {
            enableFiltering: false,
            enableSorting: false,
            enableGridMenu: false,
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            rowHeight: 30,
            columnDefs: [
                {name: 'Title', field: 'title'},
                {name: 'Status', field: 'status'},
                {name: 'Conversion', field: 'progress'}
            ]
        };

        function refresh_events() {
            $scope.events = Event.get_events();
            if($scope.events.length > 0) {
                $scope.c_event = $scope.events[$scope.events.length - 1];
            }
        }

        function refresh_players() {
            if($scope.c_event == null) {
                return;
            }
            $scope.players = Player.get_players($scope.c_event.id);
            if($scope.players.length > 0) {
                $scope.c_player = $scope.players[$scope.players.length-1];
            }
        }

        function refresh_queue() {
            if($scope.c_event == null || $scope.c_player == null) {
                return;
            }

            var status_table = [
                'Not Started',
                'Sources',
                'Cached',
                'Finished'
            ];

            var num = SourceQueue.get_queue_num($scope.c_player.id);
            var queue = SourceQueue.get_queue(num);
            var len = queue.items[0].length;
            $scope.grid_opts.minRowsToShow = len;
            $scope.grid_opts.virtualizationThreshold = len;
            var data = [];
            for(var i = 0; i < len; i++) {
                var field = queue.items[0][i];
                var source = field.source[0];
                var origin = (source.youtube_hash.length > 0)
                    ? source.youtube_hash
                    : source.other_url;
                var progress = 25 * field.status + (field.step_progress / 100) * 25;
                var o = {
                    'title': (source.title.length > 0) ? source.title : origin,
                    'status': status_table[field.status],
                    'progress': progress+' %'
                };
                data.push(o);
            }
            $scope.grid_opts.data = data;
            queue.items[0]
        }

        function init() {
            refresh_events();
            refresh_players();
            refresh_queue();

            $scope.$on(SYNC_EVENTS.queueAddFailed, function (event, args) {
                $scope.error = SourceQueue.get_last_error();
            });
            $scope.$on(SYNC_EVENTS.queuesRefresh, function(event, args) {
                refresh_queue();
            });
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

        // Form handling for url adding
        $scope.add_media = function(data) {
            if($scope.c_player == null) {
                return;
            }
            SourceQueue.add($scope.c_player.id, $scope.add_model.url);
        };
        $scope.add_model = {url: ''};
        $scope.add_error = "";


        init();
    }
]);
