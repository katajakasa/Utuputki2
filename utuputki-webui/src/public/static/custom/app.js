'use strict';

var app = angular.module(
    'utuputki',
    [
        'ngRoute',
        'ng.sockjs',
        'ui.bootstrap',
        'formly',
        'formlyBootstrap',
        'dialogs.main'
    ]
);

// Sockjs
app.value('ngSockRetry', 5000);
app.value('ngSockUrl', '/sock');

// URLs
app.config(['$routeProvider',
    function ($routeProvider) {
        $routeProvider.
            when('/login', {
                templateUrl: '/partials/login.html',
                controller: 'LoginController'
            }).
            when('/logout', {
                templateUrl: '/partials/logout.html',
                controller: 'LogoutController'
            }).
            when('/register', {
                templateUrl: '/partials/register.html',
                controller: 'RegisterController'
            }).
            when('/', {
                templateUrl: '/partials/dashboard.html',
                controller: 'DashboardController',
                requireLogin: true
            }).
            otherwise({
                redirectTo: '/login'
            });
    }
]);