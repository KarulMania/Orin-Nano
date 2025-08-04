sudo cp /home/bistek/appBiscount/services/ledProcess.service /etc/systemd/system/
sudo cp /home/bistek/appBiscount/services/biscount.service /etc/systemd/system/


sudo chmod 666 /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB1
sudo usermod -aG dialout $USER


sudo systemctl daemon-reload
sudo systemctl enable ledProcess.service
sudo systemctl start ledProcess.service
sudo systemctl enable biscount.service
sudo systemctl start biscount.service
