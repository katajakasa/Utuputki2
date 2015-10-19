'use strict';

app.service('User', [
    function () {
        function create(data) { this.data = data; }
        function destroy() { this.data = {}; }

        // Settings handling function
        function getSettings() {
            return this.data.settings;
        }

        function setSettings(settings) {
            // TODO: Upload settings to the server, and set local cache
            this.data.settings = settings;
        }

        function getUsername() { return this.data.username; }
        function getNickname() { return this.data.nickname; }
        function getEmail()    { return this.data.email; }

        return {
            create: create,
            destroy: destroy,
            getSettings: getSettings,
            setSettings: setSettings,
            getUsername: getUsername,
            getNickname: getNickname,
            getEmail: getEmail
        };
    }
]);
