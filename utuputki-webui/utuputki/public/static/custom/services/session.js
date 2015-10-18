'use strict';

app.service('Session', [
    function () {
        this.create = function (sid, uid, user) {
            this.sid = sid;
            this.uid = uid;
            this.user = user;
            localStorage['sid'] = sid;
        };
        this.destroy = function () {
            this.sid = '';
            this.uid = null;
            this.user = 0;
            localStorage.removeItem('sid');
        };

        this.hasLevel = function(level) {
            return(level >= this.user.level)
        };
        this.getLevel = function() {
            return this.user.level;
        };

        // Settings handling function
        this.getSettings = function() {
            return this.user.settings;
        };
        this.setSettings = function(settings) {
            // TODO: Upload settings to the server, and set local cache
            this.user.settings = settings;
            return;
        };

        // Player handling function
        this.getPlayers = function() {
            return this.user.players;
        };
        this.getPlayersFor = function(playlist_id) {
            var out = [];
            for(var i = 0; i < this.user.players.length; i++) {
                if(this.user.players[i].playlist_id == playlist_id) {
                    out.append(this.user.players[i]);
                }
            }
            return out;
        };
        this.createPlayerFor = function(playlist_id) {
            // Create a new player token for a given playlist
            // 1. Request token from server
            // 2. Handle response, error message(s)
            // 3. Add to local information
        };

        this.getUsername = function() { return this.user.username; };
        this.getNickname = function() { return this.user.nickname; };
        this.getEmail    = function() { return this.user.email; };

        // TODO: Functions for settings username, nickname, email
    }
]);
