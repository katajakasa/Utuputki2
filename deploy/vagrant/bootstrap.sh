#!/bin/bash

# Install mysql without it asking for root pw
export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password root"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password root"

# For nginx packages
add-apt-repository ppa:nginx/stable

# Update & fetch required system packages
apt-get -y -qq update
apt-get -y -qq install \
    npm build-essential python2.7-dev python-pip python-virtualenv \
    rabbitmq-server nginx-full mysql-server libmysqlclient-dev

# Virtual environment
ENV=/home/vagrant/env
virtualenv ${ENV}
${ENV}/bin/pip install --upgrade -r /vagrant/deploy/requirements.txt
${ENV}/bin/pip install --upgrade mysql-python

# Bower for JS library installation
ln -s /usr/bin/nodejs /usr/bin/node
npm install -g bower

# MySQL
mysql -u root -proot -e "CREATE DATABASE utuputki;"
mysql -u root -proot -e "GRANT ALL PRIVILEGES ON utuputki.* To 'utuputki'@'localhost' IDENTIFIED BY 'utuputki';"

# MQ
rabbitmqctl add_user utuputki utuputki
rabbitmqctl add_vhost utuputki
rabbitmqctl set_permissions -p utuputki utuputki ".*" ".*" ".*"

# nginx
rm -f /etc/nginx/sites-enabled/default
ln -s /vagrant/deploy/vagrant/utuputki-nginx.conf /etc/nginx/sites-available/utuputki
ln -s /vagrant/deploy/vagrant/utuputki-nginx.conf /etc/nginx/sites-enabled/utuputki

# Utuputki 2
ln -s /vagrant/deploy/vagrant/vg-utuputki.conf /etc/utuputki.conf
systemctl enable /vagrant/deploy/vagrant/utuputki-webui.service
systemctl enable /vagrant/deploy/vagrant/utuputki-downloader.service

mkdir /home/vagrant/cache
mkdir /home/vagrant/tmp
mkdir /home/vagrant/logs

chown vagrant:vagrant /home/vagrant/logs
chown vagrant:vagrant /home/vagrant/cache
chown vagrant:vagrant /home/vagrant/tmp

cd /vagrant
bower install
${ENV}/bin/alembic upgrade head
${ENV}/bin/python -m utuputki.tools create_test_admin
${ENV}/bin/python -m utuputki.tools create_event Event
${ENV}/bin/python -m utuputki.tools create_player 1 Screen

# Rock'n'roll
systemctl restart nginx
systemctl restart mysql
systemctl start utuputki-webui
sleep 1
systemctl start utuputki-downloader
