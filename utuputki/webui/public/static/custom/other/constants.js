'use strict';

app.constant('AUTH_EVENTS', {
    loginSuccess: 'auth-login-success',
    loginFailed: 'auth-login-failed',
    logoutBegin: 'auth-logout-begin',
    logoutSuccess: 'auth-logout-success',
    sessionTimeout: 'auth-session-timeout',
    notAuthenticated: 'auth-not-authenticated',
    notAuthorized: 'auth-not-authorized',
    registerSuccess: 'auth-register-success',
    registerFailed: 'auth-register-failed'
});

app.constant('SYNC_EVENTS', {
    eventAddSuccess: 'event-add-success',
    eventAddFailed: 'event-add-failed',
    eventsRefresh: 'events-refresh',
    playerAddSuccess: 'player-add-success',
    playerAddFailed: 'player-add-failed',
    playersRefresh: 'players-refresh',
    queueAddSuccess: 'queue-add-success',
    queueAddFailed: 'queue-add-failed',
    queuesRefresh: 'queues-refresh',
    mediasRefresh: 'medias-refresh',
    currentPlayerChange: 'current-player-change'
});

app.constant('USERLEVELS', {
    'none': 0,
    'user': 10,
    'admin': 20
});