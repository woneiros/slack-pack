#!/bin/bash

# Simple script that launches micro server with
# ------> security group : clouderaTest
# ------> availability zone : us-east-1a
# ------> AMI : ami-dabcfccd
# you need to choose your own security group (named above "clouderaTest") which has open ports: 8080,8088,4040,50070,22,8020
# Also make sure to set environmental variables for your EC2 KEY (KEY)

##############################################################################

# Security group with ports in accordance with 
# http://www.cloudera.com/documentation/archive/manager/4-x/4-7-2/Cloudera-Manager-Installation-Guide/cmig_install_on_EC2.html
# It aditionally has SSH access from all IPs on port 22; we may also want ports 8080, 8088, 4040, 50070 and 8020 open for all

#############################################################################

SEC_GROUP="slackpstone-2"
AVAIL_ZONE="us-east-1a"
AMI="ami-d05e75b8" 
INSTANCE_TYPE="m3.large"
KEY="EC2-US-EAST-1A" # Key for the appropriate region
NUM_INSTANCES="3"
NEWINATANCES="$(aws ec2 run-instances --image-id $AMI --key $KEY --count $NUM_INSTANCES --instance-type $INSTANCE_TYPE --security-groups $SEC_GROUP)"

check_status=$(aws ec2 describe-instance-status --instance-ids $NEWINSTACEID --query 'InstanceStatuses[*].InstanceState.Name' --output text)


until [ "$check_status" == "running" ]; do
	echo "checking..."
	sleep 1
	check_status=$(aws ec2 describe-instance-status --instance-ids $NEWINSTACEID --query 'InstanceStatuses[*].InstanceState.Name' --output text)
done

# launch ec2 t1.micro node:
# TEMP="$(aws ec2 describe-instance-status --query InstanceStatuses[*][InstanceId] --output text)"
# publicDnsName="$(aws ec2 describe-instances --instance-ids $temp --query Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicDnsName --output text)"
# ssh -i /PATH/TO/PEM root@$publicDnsName

# set elastic ip. you can do this first, one time through he AWS console
# aws ec2 associate-address --instance-id $NEWINSTACEID --public-ip xx.x.xxx.xx

# attach my volume 
# aws ec2 attach-volume --volume-id vol-xxxxxxxx --instance-id $NEWINSTACEID --device /dev/sdf

# Go Play! root @ elastic ip
# ssh -i "your_key.pem" root@xx.x.xxx.xx

#TODO: write bootsrap.sh

# To get instance ids as output
# aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceID' --output text

# To get instance ids as text
# instance_ids="$(aws ec2 describe-instance-status --query InstanceStatuses[*][InstanceId] --output text)"

#Doesn't Work - don't know how to separate the ids
# aws ec2 terminate-instances --instance-ids "$instance_ids" --output text --query 'TerminatingInstances[*].CurrentState.Name'

# aws ec2 describe-instances --instance-ids $instance_ids --query Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicDnsName --output text