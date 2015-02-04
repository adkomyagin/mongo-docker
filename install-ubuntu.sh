green=`tput setaf 2`
reset=`tput sgr0`

if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi

echo "${green}Installing packages${reset}"
[ -e /usr/lib/apt/methods/https ] || {
  apt-get update
  apt-get install apt-transport-https
}
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
echo "deb https://get.docker.com/ubuntu docker main" > /etc/apt/sources.list.d/docker.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
apt-get update >/dev/null
apt-get install -y mongodb-org-shell lxc-docker dnsmasq bridge-utils python-pip build-essential python-dev >/dev/null

update-rc.d docker defaults
pip install pymongo

echo "${green}Patching docker binaries${reset}"
service docker stop
cp docker_bin/docker /usr/bin/docker
chmod +x /usr/bin/docker
cp docker_bin/dockerinit /usr/bin/dockerinit
chmod +x /usr/bin/dockerinit

echo "${green}Disabling AppArmor${reset}"
invoke-rc.d apparmor stop
update-rc.d -f apparmor remove

echo "${green}Creating a bridge${reset}"
cat > /etc/network/interfaces.d/br0.cfg << XXX
auto br0
iface br0 inet static
pre-up brctl addbr br0
address 192.168.0.1
netmask 255.255.0.0
XXX

echo "${green}Bringing the bridge up${reset}"
brctl addbr br0

echo "${green}Setting docker to use br0${reset}"
cat >> /etc/default/docker << XXX
DOCKER_OPTS="-b=br0"
XXX

echo "${green}Setting dnsmasq to sit on br0${reset}"
echo "interface=br0" >> /etc/dnsmasq.conf

echo "${green}Enabling DHCP server in dnsmasq${reset}"
echo "dhcp-range=192.168.0.50,192.168.0.150,12h" >> /etc/dnsmasq.conf

echo "${green}Rebooting in 10 secs${reset}"
sleep 10
reboot
