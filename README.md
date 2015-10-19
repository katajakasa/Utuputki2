# Utuputki2

Utuputki 2 project.

Requirements
------------

Run all commands in utuputki-webui directory.

1. Platform requirements: python2.7, python2.7-dev, nodejs + npm + bower, RabbitMQ.
2. Python requirements: `pip install --upgrade -r deploy/requirements.txt`
3. JS requirements `bower install`

Running
-------

Again, Run all commands in utuputki-webui directory.

1. Create utuputki.conf in project root (or ~/.utuputki.conf or /etc/utuputki.conf) and edit it as necessary.
   See utuputki.conf.dist for help.
2. Run database migrations with alembic: `alembic upgrade head`.
3. Run with `python src/utuputki.py`.

Notes
-----

* Making new alembic revisions: `alembic revision --autogenerate -m "My short desc"`. Remember to check results!
* Running migrations: `alembic upgrade head`.

License
-------

MIT. See LICENSE in the repository root.
