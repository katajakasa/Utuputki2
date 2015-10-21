'use strict';

app.controller('MyQueueController', ['$scope', '$window', '$rootScope', '$location', 'Player', 'Event', 'SourceQueue', 'SYNC_EVENTS',
    function ($scope, $window, $rootScope, $location, Player, Event, SourceQueue, SYNC_EVENTS) {
        $scope.events = [];
        $scope.players = [];
        $scope.c_event = null;
        $scope.c_player = null;
        $scope.data = [];

        function redo_visibility(w) {
            $scope.grid_opts.columnDefs[1].visible = (w > 900);
            $scope.grid_opts.columnDefs[4].visible = (w > 1100);
            $scope.grid_opts.columnDefs[5].visible = (w > 1100);
            $scope.grid_opts.columnDefs[2].visible = (w > 400);
            $scope.grid_opts.columnDefs[3].visible = (w > 400);
            $scope.gridApi.core.refresh();
        }

        $scope.grid_opts = {
            enableFiltering: false,
            enableSorting: false,
            enableGridMenu: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            rowHeight: 30,
            columnDefs: [
                {name: 'Title', field: 'title'},
                {name: 'description', field: 'description'},
                {name: 'Status', field: 'status', width: 90},
                {name: 'duration', field: 'duration', width: 90},
                {name: 'Video', field: 'video', width: 240},
                {name: 'Audio', field: 'audio', width: 140}
            ],
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
            }
        };

        $scope.$watch(function(){
           return $window.innerWidth;
        }, function(value) {
            redo_visibility(value);
        });

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
                'Fetching metadata',
                'Downloading',
                'Finished',
                'Error'
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

                // Format status message
                var status = status_table[source.status];
                if(source.status == 4) {
                    status += '(' + source.message + ')'
                }

                // Format duration
                var duration = moment.duration(source.length_seconds, "seconds").format();

                var video = '';
                if(source.video.codec != '') {
                    var v = source.video;
                    video = v.codec + '@' + v.bitrate + 'kbps, ' + v.width + 'x' + v.height;
                }

                var audio = '';
                if(source.audio.codec != '') {
                    var a = source.audio;
                    audio = a.codec + '@' + a.bitrate + 'kbps';
                }

                // Add field
                $scope.grid_opts.data.push({
                    'title': source.title,
                    'description': source.description,
                    'status': status,
                    'duration': duration,
                    'video': video,
                    'audio': audio
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
