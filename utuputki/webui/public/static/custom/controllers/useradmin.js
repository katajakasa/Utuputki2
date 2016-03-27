'use strict';

app.controller('UserAdminController', ['$scope', '$rootScope', '$location', 'Event', 'UserList', 'SYNC_EVENTS',
    function ($scope, $rootScope, $location, Event, UserList, SYNC_EVENTS) {
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
                {name: 'Username', field: 'username', enableCellEdit: false},
                {name: 'Nickname', field: 'nickname'},
                {name: 'Email', field: 'email'},
                {name: 'Userlevel', field: 'level', enableCellEdit: false}
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
                UserList.edit_user(row.id, row.nickname, row.email);
                resolve(1);
            });
            $scope.gridApi.rowEdit.setSavePromise(row, promise);
            return promise;
        };

        function refresh_grid() {
            if($scope.gridApi == null)
                return;
            $scope.gridApi.core.queueRefresh();
        }

        function refresh_users() {
            $scope.grid_opts.data = UserList.get_users();
            $scope.grid_opts.minRowsToShow = $scope.grid_opts.data.length;
            $scope.grid_opts.virtualizationThreshold = $scope.grid_opts.data.length;
            refresh_grid();
        }

        function init() {
            refresh_users();
        }

        init();
    }
]);
