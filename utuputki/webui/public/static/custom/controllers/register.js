'use strict';

app.controller('RegisterController', ['$scope', '$location', '$rootScope', 'AUTH_EVENTS', 'AuthService',
    function ($scope, $location, $rootScope, AUTH_EVENTS, AuthService) {
        $scope.submit = function(new_user) {
            AuthService.register(new_user);
        };

        $scope.model = {
            username: '',
            password: '',
            nickname: '',
            email: ''
        };

        $scope.error = "";

        $scope.mfields = [
            {
                key: 'nickname',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    required: true,
                    label: 'Nickname',
                    minlength: 4,
                    maxlength: 32
                }
            },
            {
                key: 'username',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    required: true,
                    label: 'Username',
                    minlength: 6,
                    maxlength: 32
                }
            },
            {
                key: 'password',
                type: 'input',
                templateOptions: {
                    type: 'password',
                    required: true,
                    label: 'Password',
                    minlength: 8
                }
            },
            {
                key: 'email',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    label: 'Email address',
                    pattern: "(.+)@(.+)",
                    minlength: 3,
                    maxlength: 128
                }
            }
        ];

        $scope.$on(AUTH_EVENTS.registerSuccess, function (event, args) {
            $location.path('/dashboard');
        });

        $scope.$on(AUTH_EVENTS.registerFailed, function (event, args) {
            $scope.error = AuthService.get_last_error();
        });
    }
]);
