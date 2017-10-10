if [ "$EUID" -ne 0 ]
  then echo "You need to run the installation as root"
  exit
fi

useradd -M sysmon
usermod -L sysmon

apt-get install python3-pip redis-server --assume-yes

mkdir /usr/local/bin/sysmon-server
cp ../* /usr/local/bin/sysmon-server -r
chown -R sysmon /usr/local/bin/sysmon-server
chmod +x /usr/local/bin/sysmon-server/Server.py

cp sysmon.service /etc/systemd/system/

pip3 install requirements.txt
systemctl daemon-reload
