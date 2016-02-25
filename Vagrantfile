
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/wily64"
  config.vm.provision :shell, path: "deploy/vagrant/bootstrap.sh"
  config.vm.provision :shell, path: "deploy/vagrant/bootstrap_priv.sh", privileged: false
  config.vm.provision :shell, path: "deploy/vagrant/restart.sh"
  config.vm.network :forwarded_port, guest: 80, host: 55080
  config.vm.provider "virtualbox" do |v|
    v.memory = 768
  end
end