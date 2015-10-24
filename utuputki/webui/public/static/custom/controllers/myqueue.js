'use strict';

app.controller('MyQueueController', ['$scope', '$window', '$rootScope', '$location', 'Player', 'Event', 'SourceQueue', 'Session', 'SYNC_EVENTS',
    function ($scope, $window, $rootScope, $location, Player, Event, SourceQueue, Session, SYNC_EVENTS) {
        $scope.data = [];
        $scope.gridApi = null;

        function redo_visibility(w) {
            $scope.grid_opts.columnDefs[1].visible = (w > 900);
            $scope.grid_opts.columnDefs[5].visible = (w > 1100);
            $scope.grid_opts.columnDefs[6].visible = (w > 1100);
            $scope.grid_opts.columnDefs[2].visible = (w > 400);
            $scope.grid_opts.columnDefs[3].visible = (w > 400);
            $scope.grid_opts.columnDefs[4].visible = (w > 400);
            refresh_grid();
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
                {name: 'Status', field: 'status', width: 100},
                {name: 'Duration', field: 'duration', width: 90},
                {name: 'Start', field: 'projstart', width: 90},
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

        function refresh_grid() {
            if($scope.gridApi == null)
                return;
            $scope.gridApi.core.queueRefresh();
        }

        function refresh_queue() {
            var c_player = Player.get_current_player();
            if(c_player == null) {
                return;
            }

            var status_table = [
                'Not started',
                'Metadata',
                'Download',
                'On queue',
                'Error'
            ];

            $scope.grid_opts.data = [];
            $scope.grid_opts.minRowsToShow = 0;
            $scope.grid_opts.virtualizationThreshold = 0;

            var num = SourceQueue.get_queue_num(c_player.id);
            if(num < 0) {
                refresh_grid();
                return;
            }
            var queue = SourceQueue.get_queue(num);
            var len = queue.items[0].length;
            var start_sec = 0;
            for(var i = 0; i < len; i++) {
                var field = queue.items[0][i];
                var source = field.source;
                // Show only entries which have not yet been played by this player
                if(field.id <= c_player.last) {
                    continue;
                }
                // Make sure user ID matches, we only want to see our own media here.
                if(field.user_id != Session.uid) {
                    start_sec += source.length_seconds;
                    continue;
                }

                // Format status message
                var status = status_table[source.status];
                if(source.status == 4) {
                    status += '(' + source.message + ')'
                }

                // Format duration
                var duration = moment.duration(source.length_seconds, "seconds").format("hh:mm:ss", { trim: false });
                var projstart = moment.duration(start_sec, "seconds").format("hh:mm:ss", { trim: false });
                start_sec += source.length_seconds;

                // Video and audio codec information
                var video = '';
                if(source.video.codec != '') {
                    var v = source.video;
                    if(v.bitrate > 0) {
                        video = v.codec + '@' + v.bitrate + 'kbps, ' + v.width + 'x' + v.height;
                    } else {
                        video = v.codec + ', ' + v.width + 'x' + v.height;
                    }
                }
                var audio = '';
                if(source.audio.codec != '') {
                    var a = source.audio;
                    if(a.bitrate > 0) {
                        audio = a.codec + '@' + a.bitrate + 'kbps';
                    } else {
                        audio = a.codec;
                    }
                }

                // Add field
                $scope.grid_opts.data.push({
                    'title': source.title,
                    'description': source.description,
                    'status': status,
                    'duration': duration,
                    'projstart': projstart,
                    'video': video,
                    'audio': audio
                });
            }
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        function init() {
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
            $rootScope.$on(SYNC_EVENTS.currentPlayerChange, function(event, args) {
                refresh_queue();
            });
            $rootScope.$on(SYNC_EVENTS.playerPlaybackChange, function(event, args) {
                refresh_queue();
            });
        }

        // Form handling for url adding
        $scope.add_media = function(data) {
            var c_player = Player.get_current_player();
            if(c_player == null) {
                return;
            }
            SourceQueue.add(c_player.id, $scope.add_model.url);
        };
        $scope.add_model = {url: ''};
        $scope.add_error = "";


        init();
    }
]);
