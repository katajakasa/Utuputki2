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
    rabbitmq-server nginx-full mysql-server libmysqlclient-dev ffmpeg

# Set node symlink
ln -s /usr/bin/nodejs /usr/bin/node

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

# Systemctl
mkdir /usr/share/utuputki
cp /vagrant/deploy/vagrant/utuputki-downloader.service /usr/share/utuputki/
cp /vagrant/deploy/vagrant/utuputki-webui.service /usr/share/utuputki/
systemctl enable /usr/share/utuputki/utuputki-webui.service
systemctl enable /usr/share/utuputki/utuputki-downloader.service

# Utuputki 2
ln -s /vagrant/deploy/vagrant/vg-utuputki.conf /etc/utuputki.conf
