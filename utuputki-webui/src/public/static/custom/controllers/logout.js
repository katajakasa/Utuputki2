'use strict';

app.controller('LogoutController', ['$scope', 'AuthService',
    function ($scope, AuthService) {
        AuthService.logout();
    }
]);
