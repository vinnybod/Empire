#!/bin/bash
function install_powershell() {
  # Todo check for the existence of powershell
	# Deb 10.x
	if cat /etc/debian_version | grep 10.* ; then
		sudo apt-get install -y apt-transport-https curl
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" > /etc/apt/sources.list.d/microsoft.list'

		mkdir /tmp/pwshtmp
		(cd /tmp/pwshtmp && \
			wget http://http.us.debian.org/debian/pool/main/i/icu/libicu57_57.1-6+deb9u3_amd64.deb && \
			wget http://http.us.debian.org/debian/pool/main/u/ust/liblttng-ust0_2.9.0-2+deb9u1_amd64.deb && \
			wget http://http.us.debian.org/debian/pool/main/libu/liburcu/liburcu4_0.9.3-1_amd64.deb && \
			wget http://http.us.debian.org/debian/pool/main/u/ust/liblttng-ust-ctl2_2.9.0-2+deb9u1_amd64.deb && \
			wget http://security.debian.org/debian-security/pool/updates/main/o/openssl1.0/libssl1.0.2_1.0.2u-1~deb9u1_amd64.deb && \
			sudo dpkg -i *.deb)
		rm -rf /tmp/pwshtmp

		sudo apt-get update 
		sudo apt-get install -y powershell 
	# Deb 9.x
	elif cat /etc/debian_version | grep 9.* ; then
		# Install system components
		sudo apt-get install -y apt-transport-https curl
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Product feed
		sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" > /etc/apt/sources.list.d/microsoft.list'
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	# Deb 8.x
	elif cat /etc/debian_version | grep 8.* ; then
		# Install system components
		sudo apt-get install -y apt-transport-https curl gnupg
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Product feed
		sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-jessie-prod jessie main" > /etc/apt/sources.list.d/microsoft.list'
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	#Ubuntu
	elif lsb_release -d | grep -q "Ubuntu"; then
		# Read Ubuntu version
		local ubuntu_version=$( grep 'DISTRIB_RELEASE=' /etc/lsb-release | grep -o -E [[:digit:]]+\\.[[:digit:]]+ )
		# Install system components
		sudo apt-get install -y apt-transport-https curl
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Ubuntu repository
		curl https://packages.microsoft.com/config/ubuntu/$ubuntu_version/prod.list | sudo tee /etc/apt/sources.list.d/microsoft.list
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	#Kali Linux
	elif lsb_release -d | grep -q "Kali"; then
		# Download & Install prerequisites
		wget http://ftp.us.debian.org/debian/pool/main/i/icu/libicu57_57.1-6+deb9u2_amd64.deb
		dpkg -i libicu57_57.1-6+deb9u2_amd64.deb
		apt-get update && apt-get install -y curl gnupg apt-transport-https

		# Add Microsoft public repository key to APT
		curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

		# Add Microsoft package repository to the source list
		echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" | tee /etc/apt/sources.list.d/powershell.list

		# Install PowerShell package
		apt-get update && apt-get install -y powershell
	fi
	if ls /opt/microsoft/powershell/*/DELETE_ME_TO_DISABLE_CONSOLEHOST_TELEMETRY; then
		rm /opt/microsoft/powershell/*/DELETE_ME_TO_DISABLE_CONSOLEHOST_TELEMETRY
	fi
	mkdir -p /usr/local/share/powershell/Modules
	cp -r ../lib/powershell/Invoke-Obfuscation /usr/local/share/powershell/Modules
}

function install_xar() {
	# xar-1.6.1 has an incompatability with libssl 1.1.x that is patched here
	wget https://github.com/BC-SECURITY/xar/archive/xar-1.6.1-patch.tar.gz
	tar -xvf xar-1.6.1-patch.tar.gz && mv xar-xar-1.6.1-patch/xar/ xar-1.6.1/
	fi
	(cd xar-1.6.1 && ./autogen.sh)
	(cd xar-1.6.1 && ./configure)
	(cd xar-1.6.1 && make)
	(cd xar-1.6.1 && sudo make install)
}

function install_bomutils() {
	git clone https://github.com/hogliux/bomutils.git
	(cd bomutils && make)
	(cd bomutils && make install)
	chmod 755 bomutils/build/bin/mkbom && sudo cp bomutils/build/bin/mkbom /usr/local/bin/.
}

# Ask for the administrator password upfront so sudo is no longer required at Installation.
sudo -v

IFS='/' read -a array <<< pwd

if [[ "$(pwd)" != *setup ]]
then
	cd ./setup
fi

if lsb_release -d | grep -q "Kali"; then
	apt-get update
	sudo apt-get install -y make g++ python-dev python-m2crypto swig python-pip libxml2-dev default-jdk zlib1g-dev libssl1.1 build-essential libssl-dev libxml2-dev zlib1g-dev
elif lsb_release -d | grep -q "Ubuntu"; then
	sudo apt-get update
	sudo apt-get install -y make g++ python-dev python-m2crypto swig python-pip libxml2-dev default-jdk libssl1.1 libssl-dev build-essential
else
	echo "Unknown distro - Debian/Ubuntu Fallback"
	sudo apt-get update
	sudo apt-get install -y make g++ python-dev python-m2crypto swig python-pip libxml2-dev default-jdk libffi-dev libssl1.1 libssl-dev build-essential
fi

install_xar

install_bomutils

install_powershell

# set up the database schema
python ./setup_database.py

# generate a cert
./cert.sh

cd ..

echo -e '\n [*] Setup complete!\n'
