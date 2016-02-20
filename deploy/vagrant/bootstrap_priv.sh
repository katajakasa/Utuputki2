#!/bin/bash

# Paths
mkdir /home/vagrant/cache
mkdir /home/vagrant/tmp
mkdir /home/vagrant/logs

# Virtual environment
ENV=/home/vagrant/env
virtualenv ${ENV}
${ENV}/bin/pip install --upgrade -r /vagrant/deploy/requirements.txt
${ENV}/bin/pip install --upgrade mysql-python

cd /vagrant
sudo npm install -g bower
bower install
${ENV}/bin/alembic upgrade head
${ENV}/bin/python -m utuputki.tools create_test_admin
${ENV}/bin/python -m utuputki.tools create_event Event
${ENV}/bin/python -m utuputki.tools create_player 1 Screen
${ENV}/bin/python -m utuputki.tools list_players
