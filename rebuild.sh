cd src/ansible_collections/sodalite/discovery/
ansible-galaxy collection build --force
cd ../../../..
ansible-galaxy collection install src/ansible_collections/sodalite/discovery/sodalite-discovery-0.1.0.tar.gz --force

cd src/ansible_collections/sodalite/hpc/
ansible-galaxy collection build --force
cd ../../../..
ansible-galaxy collection install src/ansible_collections/sodalite/hpc/sodalite-hpc-0.1.0.tar.gz --force