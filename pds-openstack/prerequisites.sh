#!/bin/bash
echo "Installing opera"
python3 -m pip install --upgrade pip
python3 -m pip install opera[openstack]==0.6.4 docker

echo
echo "Installing required Ansible roles"
ansible-galaxy install geerlingguy.pip,2.0.0 --force
ansible-galaxy install geerlingguy.docker,2.9.0 --force
ansible-galaxy install geerlingguy.repo-epel,3.0.0 --force

echo
echo "Cloning modules"
rm -r -f modules/
git clone -b 3.4.1 https://github.com/SODALITE-EU/iac-modules.git modules/

echo "Please enter email for SODALITE certificate: "
read EMAIL_INPUT
export SODALITE_EMAIL=$EMAIL_INPUT

echo "Checking TLS key and certificate..."
FILE_KEY=modules/docker/artifacts/ca.key
if [ -f "$FILE_KEY" ]; then
    echo "TLS key file already exists."
else
    echo "TLS key does not exist. Generating..."
    openssl genrsa -out $FILE_KEY 4096
fi
FILE_CRT=modules/docker/artifacts/ca.crt
if [ -f "$FILE_CRT" ]; then
    echo "TLS certificate file already exists."
else
    echo "TLS certificate does not exist. Generating..."
    openssl req -new -x509 -key $FILE_KEY -out $FILE_CRT -subj "/C=SI/O=XLAB/CN=$SODALITE_EMAIL" 2>/dev/null
fi

unset SODALITE_EMAIL