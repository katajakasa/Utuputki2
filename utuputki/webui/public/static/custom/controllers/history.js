'use strict';

app.controller('HistoryController', ['$scope', '$window', '$rootScope', '$location', 'Player', 'Event', 'Playlist', 'Session', 'SYNC_EVENTS',
    function ($scope, $window, $rootScope, $location, Player, Event, Playlist, Session, SYNC_EVENTS) {
        $scope.gridApi = null;

        $scope.grid_opts = {
            enableFiltering: false,
            enableSorting: false,
            enableGridMenu: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            rowHeight: 30,
            columnDefs: [
                {name: 'Id', field: 'id', width: 60},
                {name: 'Title', cellTemplate: '<div class="ui-grid-cell-contents"><a href="{{row.entity.url}}">{{row.entity.title}}</a></div>'},
                {name: 'Description', field: 'description'},
                {name: 'Duration', field: 'duration', width: 90}
            ],
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
            }
        };
        $scope.grid_opts.data = [];

        function redo_visibility(w) {
            if($scope.grid_opts.data.length > 0) {
                $scope.grid_opts.columnDefs[0].visible = (w > 400);
                $scope.grid_opts.columnDefs[2].visible = (w > 900);
                $scope.grid_opts.columnDefs[3].visible = (w > 500);
                $scope.grid_opts.columnDefs[4].visible = (w > 400);
                refresh_grid();
            }
        }

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

        function refresh_playlist() {
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

            var playlist = Playlist.get_playlist();
            var len = playlist.length;
            for(var i = 0; i < len; i++) {
                var field = playlist[i];
                var source = field.source;

                // Format status message
                var status = status_table[source.status];
                if(source.status == 4) {
                    status += '(' + source.message + ')'
                }

                // Format duration
                var duration = moment.duration(source.length_seconds, "seconds").format("hh:mm:ss", { trim: false });

                // Add field
                $scope.grid_opts.data.push({
                    'id': i+1,
                    'title': source.title,
                    'description': source.description,
                    'status': status,
                    'duration': duration,
                    'url': 'http://youtu.be/'+source.youtube_hash
                });
            }
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        $scope.export = function() {
            var c_player = Player.get_current_player();
            if(c_player == null) {
                return;
            }

            var playlist = Playlist.get_playlist();
            var out = [];
            for(var i = 0; i < playlist.length; i++) {
                var field = playlist[i];
                var source = field.source;
                var duration = moment.duration(source.length_seconds, "seconds").format("hh:mm:ss", { trim: false });
                out.push([
                    source.id,
                    source.title,
                    duration,
                    'http://youtu.be/'+source.youtube_hash,
                    source.description
                ]);
            }
            exportToCsv("playlist.csv", out);
        };

        function init() {
            var c_player = Player.get_current_player();
            Playlist.query(c_player.id);

            $rootScope.$on(SYNC_EVENTS.mediasRefresh, function(event, args) {
                refresh_playlist();
            });
            $rootScope.$on(SYNC_EVENTS.currentPlayerChange, function(event, args) {
                var c_player = Player.get_current_player();
                if(c_player != null) {
                    Playlist.query(c_player.id);
                }
            });
            $rootScope.$on(SYNC_EVENTS.playerPlaybackChange, function(event, args) {
                refresh_playlist();
            });
        }

        init();
    }
]);
