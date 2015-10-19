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
    }
]);
