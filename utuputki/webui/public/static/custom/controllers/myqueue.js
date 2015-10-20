'use strict';

app.controller('MyQueueController', ['$scope', '$rootScope', '$location', 'Player', 'Event', 'SourceQueue', 'SYNC_EVENTS',
    function ($scope, $rootScope, $location, Player, Event, SourceQueue, SYNC_EVENTS) {
        $scope.events = [];
        $scope.players = [];
        $scope.c_event = null;
        $scope.c_player = null;
        $scope.data = [];

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

        $scope.getTableHeight = function() {
            var rowHeight = 30; // your row height
            var headerHeight = 30; // your header height
            return {
                height: ($scope.grid_opts.data.length * rowHeight + headerHeight) + "px"
            };
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
            if($scope.c_player == null) {
                return;
            }

            var status_table = [
                'Not Started',
                'Sourced',
                'Cached',
                'Finished'
            ];

            var num = SourceQueue.get_queue_num($scope.c_player.id);
            if(num < 0) {
                return;
            }
            var queue = SourceQueue.get_queue(num);
            var len = queue.items[0].length;
            $scope.grid_opts.data = [];
            for(var i = 0; i < len; i++) {
                var field = queue.items[0][i];
                var source = field.source[0];
                var origin = (source.youtube_hash.length > 0)
                    ? source.youtube_hash
                    : source.other_url;
                var progress = 25 * field.status + (field.step_progress / 100) * 25;
                $scope.grid_opts.data.push({
                    'title': (source.title.length > 0) ? source.title : origin,
                    'status': status_table[field.status],
                    'progress': progress+' %'
                });
            }
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            $scope.refresh = true;
        }

        function init() {
            refresh_events();
            refresh_players();
            refresh_queue();

            $rootScope.$on(SYNC_EVENTS.queueAddFailed, function (event, args) {
                $scope.error = SourceQueue.get_last_error();
            });
            $rootScope.$on(SYNC_EVENTS.queueAddSuccess, function (event, args) {
                $scope.error = "";
                $scope.add_model.url = '';
            });
            $rootScope.$on(SYNC_EVENTS.queuesRefresh, function(event, args) {
                refresh_queue();
            });
            $rootScope.$on(SYNC_EVENTS.playersRefresh, function(event, args) {
                refresh_players();
                refresh_queue();
            });
            $rootScope.$on(SYNC_EVENTS.eventsRefresh, function(event, args) {
                refresh_events();
                refresh_players();
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
