'use strict';

app.controller('EventAdminController', ['$scope', '$rootScope', '$location', 'Event', 'SYNC_EVENTS',
    function ($scope, $rootScope, $location, Event, SYNC_EVENTS) {
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
                {name: 'Visible', field: 'visible', type: 'boolean'}
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
                Event.edit_event(row.id, row.name, row.visible);
                resolve(1);
            });
            $scope.gridApi.rowEdit.setSavePromise(row, promise);
            return promise;
        };

        $scope.add_row = function() {
            Event.add_event();
        };

        function refresh_grid() {
            if($scope.gridApi == null)
                return;
            $scope.gridApi.core.queueRefresh();
        }

        function refresh_events() {
            $scope.grid_opts.data = Event.get_events();
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        function init() {
            refresh_events();

            $rootScope.$on(SYNC_EVENTS.eventsRefresh, function(event, args) {
                refresh_events();
            });
        }

        init();
    }
]);
