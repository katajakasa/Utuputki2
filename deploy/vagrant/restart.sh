#!/bin/bash

# Rock'n'roll
systemctl restart nginx
systemctl restart mysql
systemctl restart utuputki-webui
sleep 1
systemctl restart utuputki-downloader
