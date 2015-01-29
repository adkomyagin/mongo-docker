if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi

echo "Installing packages"
[ -e /usr/lib/apt/methods/https ] || {
  apt-get update
  apt-get install apt-transport-https
}
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
echo "deb https://get.docker.com/ubuntu docker main" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y lxc-docker

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
apt-get update
apt-get install -y mongodb-org-shell

apt-get install -y dnsmasq
apt-get install -y brctl

apt-get install -y pip
pip install pymongo

echo "Overriding the 1.4.1-dev version of Docker"
wget https://master.dockerproject.com/linux/amd64/docker-1.4.1-dev -O docker
chmod +x docker
mv docker /usr/bin/docker

echo "Disabling AppArmor"
invoke-rc.d apparmor kill
update-rc.d -f apparmor remove

echo "Creating a bridge"
cat > /etc/network/interfaces.d/br0.cfg << XXX
auto br0
iface br0 inet static
address 192.168.0.1
netmask 255.255.0.0
XXX

echo "Bringing the bridge up"
brctl addbr br0

echo "Setting docker to use br0"
cat >> /etc/default/docker << XXX
DOCKER_OPTS="-b=br0"
XXX

echo "Setting dnsmasq to sit on br0"
echo "interface=br0" >> /etc/dnsmasq.conf

echo "Enabling DHCP server in dnsmasq"
echo "dhcp-range=192.168.0.50,192.168.0.150,12h" >> /etc/dnsmasq.conf

echo "Rebooting in 3 secs"
sleep 3
reboot
