#!/bin/sh

sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update -y
sudo apt-get install oracle-java8-installer -y

echo 'JAVA_HOME="/usr/lib/jvm/java-8-oracle"' | sudo tee -a /etc/environment
sudo source /etc/environment

wget http://ftp.wayne.edu/apache/kafka/0.10.0.0/kafka_2.11-0.10.0.0.tgz
sudo tar -xzf kafka_2.11-0.10.0.0.tgz 
