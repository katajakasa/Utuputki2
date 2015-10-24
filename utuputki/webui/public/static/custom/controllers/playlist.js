'use strict';

app.controller('PlaylistController', ['$scope', '$window', '$rootScope', '$location', 'Player', 'Event', 'Playlist', 'Session', 'SYNC_EVENTS',
    function ($scope, $window, $rootScope, $location, Player, Event, Playlist, Session, SYNC_EVENTS) {
        $scope.events = [];
        $scope.players = [];
        $scope.c_event = null;
        $scope.c_player = null;
        $scope.data = [];
        $scope.gridApi = null;

        function redo_visibility(w) {
            $scope.grid_opts.columnDefs[1].visible = (w > 900);
            $scope.grid_opts.columnDefs[2].visible = (w > 400);
            $scope.grid_opts.columnDefs[3].visible = (w > 400);
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
                {name: 'Status', field: 'status', width: 90},
                {name: 'duration', field: 'duration', width: 90}
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
                Playlist.query($scope.c_player.id);
            }
        }

        function refresh_grid() {
            if($scope.gridApi == null)
                return;
            $scope.gridApi.core.queueRefresh();
        }

        function refresh_playlist() {
            if($scope.c_player == null) {
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
                // Show only entries which have not yet been played by this player
                if(field.id <= $scope.c_player.last) {
                    continue;
                }
                var source = field.source;

                // Format status message
                var status = status_table[source.status];
                if(source.status == 4) {
                    status += '(' + source.message + ')'
                }

                // Format duration
                var duration = moment.duration(source.length_seconds, "seconds").format("mm:ss");

                // Add field
                $scope.grid_opts.data.push({
                    'title': source.title,
                    'description': source.description,
                    'status': status,
                    'duration': duration
                });
            }
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        function init() {
            refresh_events();
            refresh_players();
            refresh_playlist();

            $rootScope.$on(SYNC_EVENTS.mediasRefresh, function(event, args) {
                refresh_playlist();
            });
            $rootScope.$on(SYNC_EVENTS.playersRefresh, function(event, args) {
                refresh_players();
            });
            $rootScope.$on(SYNC_EVENTS.eventsRefresh, function(event, args) {
                refresh_events();
                refresh_players();
            });
        }

        $scope.sel_event = function(event) {
            $scope.c_event = event;
            refresh_players();
        };

        $scope.sel_player = function(player) {
            $scope.c_player = player;
            Playlist.query($scope.c_player.id);
        };

        init();
    }
]);
