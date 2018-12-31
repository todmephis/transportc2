#!/usr/bin/env bash
################################################################################
# TransportC2 Setup Script
#
# Usage:
#	./setup.sh
#	./setup.sh uninstall
#	./setup.sh troubleshoot
################################################################################

#Define Variables
PYTHON_EXEC="transportc2.py"
PROGRAM="transportc2"
SERVICE="/etc/systemd/system/${PROGRAM}.service"
DIRECTORY="/opt/${PROGRAM}"

#Check if Script run as root
if [[ $(id -u) != 0 ]]; then
	echo -e "\n[!] Setup script needs to run as root\n\n"
	exit 0
fi

# Check for uninstall
if [[ $1 && $1 == "uninstall" ]]; then
    echo "[*] Uninstalling TransportC2 :("
    systemctl stop transportc2.service
    systemctl disable transportc2.service
    rm "${SERVICE}"
    rm -rf "${DIRECTORY}"
    echo "[+] Come Back any time!"
    exit
fi

# Running into issues? Delete all cached data
if [[ $1 && $1 == "troubleshoot" ]]; then
	find "${DIRECTORY}" -iname "__"* -exec rm -rfv {} \;
	exit
fi

# Else, run install script
echo "[+] Starting TransportC2 setup script"
apt-get install python3
apt-get install python3-pip
pip3 install Flask
pip3 install flask-login

################################################################################
# Setup service
################################################################################
# Create service file
echo "Description=TransportC2" > transportc2.service
echo "After=multi-user.target" >> transportc2.service
echo "[Service]" >> transportc2.service
echo "Type=idle" >> transportc2.service
echo "WorkingDirectory=${DIRECTORY}" >> transportc2.service
echo "ExecStart=${DIRECTORY}/${PYTHON_EXEC}" >> transportc2.service
echo "[Install]" >> transportc2.service
echo "WantedBy=multi-user.target" >> transportc2.service

# Move to proper location + set file permissions
chmod +x "../transportc2.py"

# Delete existing if already exists:
if [ -f "${SERVICE}" ]; then
    rm -rf "${SERVICE}"
fi

cp "${PROGRAM}.service" "${SERVICE}"
chmod 644 "${SERVICE}"
systemctl daemon-reload

# Generate Key and Cert File for HTTPS
echo -e "\n \n \n \n \n \n"|openssl req  -nodes -new -x509  -keyout ../server/AdminServer/certs/key.pem -out ../server/AdminServer/certs/cert.crt

################################################################################
# Move to OPT
################################################################################
if [ -d "${DIRECTORY}" ]; then
    # Remove $DIRECTORY if $DIRECTORY exists.
    echo -e "\n[*] removing existing ${DIRECTORY}"
    rm -rf "${DIRECTORY}"
fi

mkdir "${DIRECTORY}"
cd ../../
#Copy the source files to the $DIRECTORY
cp -r "${PROGRAM}" "/opt/"

echo "[+] Setup Complete!"
echo "[*] Use the following commands to start the service:"
echo "  sudo systemctl start transportc2.service"
echo "  sudo systemctl status transportc2.service"
echo -e "  sudo systemctl stop transportc2.service\n\n"
