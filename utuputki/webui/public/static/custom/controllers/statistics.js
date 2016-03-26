'use strict';

app.controller('StatisticsController', ['$scope', '$location', '$rootScope', 'SYNC_EVENTS', 'Statistics',
    function ($scope, $location, $rootScope, SYNC_EVENTS, Statistics) {
        $scope.received_api = null;
        $scope.given_api = null;

        $scope.received_opts = {
            enableFiltering: false,
            enableSorting: false,
            enableGridMenu: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            rowHeight: 30,
            columnDefs: [
                {name: '#', field: 'number', width: 100},
                {name: 'Amount', field: 'amount', width: 100},
                {name: 'Name', field: 'name'}
            ],
            onRegisterApi: function(gridApi){
                $scope.received_api = gridApi;
            }
        };

        $scope.given_opts = {
            enableFiltering: false,
            enableSorting: false,
            enableGridMenu: false,
            enableColumnMenus: false,
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            rowHeight: 30,
            columnDefs: [
                {name: '#', field: 'number', width: 100},
                {name: 'Amount', field: 'amount', width: 100},
                {name: 'Name', field: 'name'}
            ],
            onRegisterApi: function(gridApi){
                $scope.given_api = gridApi;
            }
        };

        $scope.getTableHeight = function(opts) {
            var rowHeight = 30; // your row height
            var headerHeight = 30; // your header height
            return {
                height: (opts.data.length * rowHeight + headerHeight) + "px"
            };
        };

        $scope.show_given_table = function() {
            return ($scope.given_opts.length > 0);
        };

        $scope.show_received_table = function() {
            return ($scope.received_opts.length > 0);
        };

        function refresh_most_given() {
            $scope.given_opts.data = Statistics.get_most_given();
            $scope.given_opts.minRowsToShow = $scope.given_opts.data.length;
            $scope.given_opts.virtualizationThreshold = $scope.given_opts.data.length;
        }

        function refresh_most_received() {
            $scope.received_opts.data = Statistics.get_most_received();
            $scope.received_opts.minRowsToShow = $scope.received_opts.data.length;
            $scope.received_opts.virtualizationThreshold = $scope.received_opts.data.length;
        }

        function init() {
            refresh_most_given();
            refresh_most_received();
            $rootScope.$on(SYNC_EVENTS.statsRefresh, function(event, args) {
                refresh_most_given();
                refresh_most_received();
            });
        }

        init();
    }
]);
