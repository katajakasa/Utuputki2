'use strict';

app.factory('Playlist', ['$location', '$rootScope', 'SockService', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var medias = [];

        function queue_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == 'fetchall') {
                    medias = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.mediasRefresh);
                    return;
                }
                console.error("Unknown incoming queue packet subtype!")
            }
        }

        function setup() {
            SockService.add_recv_handler('playlist', queue_event);
        }

        function get_media(media_id) {
            for(var i = 0; i < medias.length; i++) {
                if(medias[i].id == media_id) {
                    return medias[i];
                }
            }
            return null;
        }

        function get_playlist() {
            return medias;
        }

        function query(player_id) {
            SockService.send_msg('playlist', {'player_id': player_id}, 'fetchall');
        }

        function get_last_error() {
            return last_error;
        }

        return {
            setup: setup,
            query: query,
            get_playlist: get_playlist,
            get_last_error: get_last_error,
            get_media: get_media
        };
    }
]);
