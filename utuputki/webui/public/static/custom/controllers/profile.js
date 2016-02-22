'use strict';

app.controller('ProfileController', ['$scope', '$location', '$rootScope', 'User', 'AUTH_EVENTS', 'AuthService',
    function ($scope, $location, $rootScope, User, AUTH_EVENTS, AuthService) {
        $scope.submit = function(profile) {
            AuthService.update_profile(profile);
        };

        $scope.model = {
            password: '',
            password2: '',
            nickname: User.getNickname(),
            email: User.getEmail()
        };

        $scope.error = "";
        $scope.success = "";

        $scope.mfields = [
            {
                key: 'nickname',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    required: true,
                    label: 'Nickname'
                }
            },
            {
                key: 'email',
                type: 'input',
                templateOptions: {
                    type: 'text',
                    label: 'Email address'
                }
            },
            {
                key: 'password',
                type: 'input',
                templateOptions: {
                    type: 'password',
                    required: false,
                    label: 'Password'
                }
            },
            {
                key: 'password2',
                type: 'input',
                templateOptions: {
                    type: 'password',
                    required: false,
                    label: 'Password (again)'
                }
            }
        ];

        $scope.$on(AUTH_EVENTS.profileSuccess, function(event, args) {
            $scope.success = "Profile successfully updated!";
            $scope.error = "";
        });

        $scope.$on(AUTH_EVENTS.profileFailed, function(event, args) {
            $scope.error = AuthService.get_last_error();
            $scope.success = "";
        });
    }
]);
