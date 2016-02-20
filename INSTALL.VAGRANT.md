# Vagrant-based Installation

## 1. Requirements

Install Vagrant. The method depends on your OS.

## 2. Installation

1. Get Utuputki2 sources and install them. Either git clone or extract tarball.
2. Change `deploy/vagrant/vg-utuputki.conf` as necessary.
3. Navigate to the source directory, and run `vagrant up`. This will provision the virtual machine. May take a few
   minutes.
4. Open up your browser and navigate to "http://localhost:55080". Default username and password is "admin".

## 3. Other

* For connecting to the vagrant virtualbox, use `vagrant ssh`.
* To halt, use `vagrant halt`.
* To completely destroy the box, use `vagrant destroy`.

## 4. Notes

Please note that currently the Vagrant installation method is only meant for testing and development! It would probably
be possible to use it for production, but currently that is out-of-scope for this installation file.
