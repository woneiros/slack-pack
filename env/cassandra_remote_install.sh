#!/bin/sh

# Bash scrip to set up an aws instance for kafka

# Install java
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update -y
sudo apt-get install oracle-java8-installer -y
#etc.

# Add to apt sources
echo deb http://debian.datastax.com/datastax-ddc 3.9 main | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
# Add datastax as trusted source
wget -qO - http://debian.datastax.com/debian/repo_key | sudo apt-key add -
# Update apt
sudo apt-get update
# Install cassandra (it is automatically running as a service)
sudo apt-get install datastax-ddc -yes
# Stop the service
sudo service cassandra stop
# Delete any logs
sudo rm -rf /var/lib/cassandra/data/system/*

