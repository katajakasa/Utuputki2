'use strict';

app.controller('LoginController', ['$scope', '$location', '$rootScope', 'AUTH_EVENTS', 'AuthService',
    function ($scope, $location, $rootScope, AUTH_EVENTS, AuthService) {
        $scope.submit = function(credentials) {
            AuthService.login(credentials);
        };

        $scope.model = {
            username: '',
            password: ''
        };

        $scope.error = "";

        $scope.mfields = [
            {
                key: 'username',
                type: 'input',
                templateOptions: {
                    type: "text",
                    required: true,
                    label: 'Username'
                }
            },
            {
                key: 'password',
                type: 'input',
                templateOptions: {
                    required: true,
                    type: 'password',
                    label: 'Password'
                }
            }
        ];

        $scope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
            $location.path('/dashboard');
        });

        $scope.$on(AUTH_EVENTS.loginFailed, function (event, args) {
            $scope.error = AuthService.get_last_error();
        });
    }
]);
