#!/bin/bash

# Simple script that launches AWS server with

##############################################################################

# Make sure that you have defined locally the path to your pem file in a file
# called "PATH_TO_PEM"

#############################################################################

# launch first ec2 node found:
TEMP="$(aws ec2 describe-instance-status --query 'InstanceStatuses[*][InstanceId]' --output text)"
publicDnsName="$(aws ec2 describe-instances --instance-ids $temp --query 'Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicDnsName' --output text)"
ssh -i $PATH_TO_PEM root@$publicDnsName

# set elastic ip. you can do this first, one time through he AWS console
# aws ec2 associate-address --instance-id $NEWINSTACEID --public-ip xx.x.xxx.xx

# attach my volume 
# aws ec2 attach-volume --volume-id vol-xxxxxxxx --instance-id $NEWINSTACEID --device /dev/sdf

# Go Play! root @ elastic ip
# ssh -i "your_key.pem" root@xx.x.xxx.xx

#TODO: write bootsrap.sh
