#!/usr/bin/env bash
# execute as root
# we expect ec2-user to be present on the system
mkdir /var/log/wgen/
chmod 770 /var/log/wgen/
chown ec2-user:ec2-user /var/log/wgen/
cp wgen.cron /etc/cron.d/
