# Utuputki2

Utuputki 2 project.

Requirements
------------

Run all commands in utuputki-webui directory.

1. Platform requirements: python2.7, python2.7-dev, nodejs + npm + bower, RabbitMQ.
2. Python requirements: `pip install --upgrade -r deploy/requirements.txt`
3. JS requirements `bower install`

Setting up RabbitMQ
-------------------

A quick example (edit as necessary):

1. sudo rabbitmqctl add_user utuputki utuputki
2. sudo rabbitmqctl add_vhost utuputki
3. sudo rabbitmqctl set_permissions -p utuputki utuputki ".*" ".*" ".*"

Running
-------

Again, Run all commands in utuputki-webui directory.

1. Create utuputki.conf in project root (or ~/.utuputki.conf or /etc/utuputki.conf) and edit it as necessary.
   See utuputki.conf.dist for help.
2. Run database migrations with alembic: `alembic upgrade head`.
3. Create an admin user, a new event and a player for the event (currently via the tools module, see below)
4. Run the apps (see below). Enjoy!

To start the apps:
* `python -m utuputki.webui.webui_main` to run the main www-ui
* `python -m utuputki.downloader.downloader_main` to start the downloader daemon.

To run the tools (for creating the event and a player)
* `python -m utuputki.tools <command>`

Notes
-----

* Making new alembic revisions: `alembic revision --autogenerate -m "My short desc"`. Remember to check results!
* Running migrations: `alembic upgrade head`.

License
-------

MIT. See LICENSE in the repository root.
