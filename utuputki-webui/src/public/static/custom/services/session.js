'use strict';

app.service('Session', [
    function () {
        this.create = function (sid, uid, level) {
            this.sid = sid;
            this.uid = uid;
            this.level = level;
            localStorage['sid'] = sid;
        };
        this.destroy = function () {
            this.sid = '';
            this.uid = null;
            this.level = 0;
            localStorage.removeItem('sid');
        };
    }
]);
