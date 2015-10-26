# Utuputki2

Utuputki 2 Server and Downloader modules.

Utuputki2 is a communal LAN-party Screen management software. Users may queue youtube-videos to playlist, which the player
then show on the screen in order. This repository contains the WWW-UI and Downloader/conversion daemon. See
Utuputki2-client project for the player component.

![Screenshot](https://raw.githubusercontent.com/katajakasa/Utuputki2/master/media/screen.png)

## Installing

Run all commands in utuputki-webui directory.

### Requirements

#### Debian/Ubuntu

1. `sudo apt-get install npm python2.7-dev python-pip python-virtualenv rabbitmq-server`. Also install an SQL server of your choice (mysql and sqlite3 tested). For RabbitMQ configuration, see below.
2. Install bower, eg. `sudo npm install -g bower`. Please see [Bower installation  instructions](http://bower.io/#install-bower) for details
3. Create a virtualenv `virtualenv /path/to/virtualenv/utuputki2` and activate it `source /path/to/virtualenv/utuputki2/bin/activate`. See [virtualenv documentation](https://virtualenv.pypa.io/en/latest/) for details.
4. Install python requirements: `pip install --upgrade -r deploy/requirements.txt`.
5. Install JS requirements `bower install`.

#### Windows

No instructions yet. User needs to get and install the packages by himself. It IS possible to run on windows though!

### Setting up the servers

1. Create utuputki.conf in project root (or ~/.utuputki.conf or /etc/utuputki.conf) and edit it as necessary.
   See utuputki.conf.dist for help.
2. Run database migrations with alembic: `alembic upgrade head`.
3. Create an admin user: `python -m utuputki.tools create_admin`. Admin user can upload any length videos and manage playback, while normal users will be limited in video duration and management options.
4. Create a new event: `python -m utuputki.tools create_event`. There can be multiple events, eg. "My Lanparty 2015", "New lan party 2016", etc.
5. Create a new player for the event `python -m utuputki.tools create_player`. A sinle event can have multiple players, for example if there are multiple screens.
6. Run the apps (see below). Enjoy!

### Setting up RabbitMQ

A quick example below (edit as necessary). See [rabbitmqctl man page](https://www.rabbitmq.com/man/rabbitmqctl.1.man.html) and [RabbitMQ manual](https://www.rabbitmq.com/download.html) for more instructions.

1. Create a new user with a password: `sudo rabbitmqctl add_user utuputki utuputki`
2. Create a new virtual host: `sudo rabbitmqctl add_vhost utuputki`
3. Grant all rights to user on vhost: `sudo rabbitmqctl set_permissions -p utuputki utuputki ".*" ".*" ".*"`

## Running

Run all commands in utuputki-webui directory.

To start the apps:
* `python -m utuputki.webui.webui_main` to run the main www-ui
* `python -m utuputki.downloader.downloader_main` to start the downloader daemon.

To run the tools (for creating the event and a player)
* `python -m utuputki.tools <command>`

## Nginx

It is generally a good idea to let a web server like Nginx to server all your video files and static content, freeing tornado to server sockjs connections. An example nginx configuration can be found at deploy/utuputki-nginx.conf.

## License

MIT. See LICENSE in the repository root.
