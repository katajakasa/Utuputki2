Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/wily64"
  config.vm.provision :shell, path: "deploy/vagrant/bootstrap.sh"
  config.vm.network :forwarded_port, guest: 80, host: 55080
end