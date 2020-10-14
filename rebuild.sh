cd ansible_collections/sodalite/discovery/
ansible-galaxy collection build --force
cd ../../..
ansible-galaxy collection install ansible_collections/sodalite/discovery/sodalite-discovery-0.1.0.tar.gz --force