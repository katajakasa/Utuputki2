'use strict';

var app = angular.module(
    'utuputki',
    [
        'ngRoute',
        'ng.sockjs',
        'ui.bootstrap',
        'ui.grid',
        'ui.grid.autoResize',
        'ui.grid.edit',
        'ui.grid.rowEdit',
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
    function($routeProvider) {
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
            when('/history', {
                templateUrl: '/partials/history.html',
                controller: 'HistoryController',
                requireLogin: true
            }).
            when('/playlist', {
                templateUrl: '/partials/playlist.html',
                controller: 'PlaylistController',
                requireLogin: true
            }).
            when('/stats', {
                templateUrl: '/partials/fame.html',
                controller: 'StatisticsController',
                requireLogin: true
            }).
            when('/profile', {
                templateUrl: '/partials/profile.html',
                controller: 'ProfileController',
                requireLogin: true
            }).
            when('/eventadmin', {
                templateUrl: '/partials/eventadmin.html',
                controller: 'EventAdminController',
                requireLogin: true,
                requireAdmin: true
            }).
            when('/playeradmin', {
                templateUrl: '/partials/playeradmin.html',
                controller: 'PlayerAdminController',
                requireLogin: true,
                requireAdmin: true
            }).
            when('/', {
                templateUrl: '/partials/myqueue.html',
                controller: 'MyQueueController',
                requireLogin: true
            }).
            otherwise({
                redirectTo: '/login'
            });
    }
]);