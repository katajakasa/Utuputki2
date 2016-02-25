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
    registerFailed: 'auth-register-failed',
    profileSuccess: 'auth-profile-success',
    profileFailed: 'auth-profile-failed'
});

app.constant('SYNC_EVENTS', {
    eventAddSuccess: 'event-add-success',
    eventAddFailed: 'event-add-failed',
    eventsRefresh: 'events-refresh',
    eventAdded: 'event-added',
    eventsEdited: 'events-edited',
    playerAddSuccess: 'player-add-success',
    playerAddFailed: 'player-add-failed',
    playersRefresh: 'players-refresh',
    playerAdded: 'player-added',
    playersEdited: 'players-edited',
    queueAddSuccess: 'queue-add-success',
    queueAddFailed: 'queue-add-failed',
    queuesRefresh: 'queues-refresh',
    mediasRefresh: 'medias-refresh',
    currentPlayerChange: 'current-player-change',
    playerPlaybackChange: 'current-player-song-change',
    playerSkipCountChange: 'current-player-req-skip-count-change',
    statsRefresh: 'statis-refresh'
});

app.constant('USERLEVELS', {
    'none': 0,
    'user': 10,
    'admin': 20
});