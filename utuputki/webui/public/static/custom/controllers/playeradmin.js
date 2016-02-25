'use strict';

app.controller('PlayerAdminController', ['$scope', '$rootScope', '$location', 'Event', 'Player', 'SYNC_EVENTS',
    function ($scope, $rootScope, $location, Event, Player, SYNC_EVENTS) {
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
                {name: 'ID', field: 'id', width: 100, enableCellEdit: false},
                {name: 'Name', field: 'name'},
                {name: 'Token', field: 'token', enableCellEdit: false}
            ],
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
                gridApi.rowEdit.on.saveRow($scope, $scope.save_rows);
            }
        };

        $scope.getTableHeight = function() {
            var rowHeight = 30; // your row height
            var headerHeight = 30; // your header height
            return {
                height: ($scope.grid_opts.data.length * rowHeight + headerHeight) + "px"
            };
        };

        $scope.save_rows = function(row) {
            var promise = new Promise(function(resolve, reject) {
                Player.edit_player(row.id, row.name);
                resolve(1);
            });
            $scope.gridApi.rowEdit.setSavePromise(row, promise);
            return promise;
        };

        $scope.add_row = function() {
            Player.add_player(Event.get_selected_event());
        };

        function refresh_grid() {
            if($scope.gridApi == null)
                return;
            $scope.gridApi.core.queueRefresh();
        }

        function refresh_players() {
            $scope.grid_opts.data = Player.get_players(Event.get_selected_event());
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        function init() {
            refresh_players();

            $rootScope.$on(SYNC_EVENTS.playerAdded, function(event, args) {
                refresh_players();
            });
        }

        init();
    }
]);
