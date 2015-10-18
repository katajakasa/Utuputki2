'use strict';

app.factory('AuthService', ['$location', '$rootScope', 'Session', 'AUTH_EVENTS', 'SockService',
    function ($location, $rootScope, AUTH_EVENTS, SockService) {
        function setup() {

        }

        function add(url) {

        }

        function remove(remove) {

        }

        function getUnplayed() {

        }

        return {
            setup: setup,
            add: add,
            remove: remove
        };
    }
]);