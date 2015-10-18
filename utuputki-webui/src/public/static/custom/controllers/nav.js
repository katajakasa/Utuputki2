'use strict';

app.controller('NavController', ['$scope', '$location', 'AuthService',
    function ($scope, $location, AuthService) {
        $scope.sites = [
            {url: '/', name: 'My Queue', requireLogin: true},
            {url: '/playlist', name: 'Playlist', requireLogin: true},
            {url: '/history', name: 'History', requireLogin: true},
            {url: '/login', name: 'Login', requireLogin: false},
            {url: '/register', name: 'Register', requireLogin: false},
            {url: '/logout', name: 'Logout', requireLogin: true}
        ];

        $scope.is_active = function (loc) {
            return (loc === $location.path());
        };
        $scope.is_visible = function (url) {
            for (var i = 0; i < $scope.sites.length; i++) {
                if ($scope.sites[i].url == url) {
                    if ($scope.sites[i].requireLogin) {
                        return (AuthService.is_authenticated());
                    } else {
                        return (!AuthService.is_authenticated());
                    }
                }
            }
            return true;
        }
    }
]);
