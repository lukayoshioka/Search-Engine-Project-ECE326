sudo apt-get update -y
sudo apt-get install python3-venv -y
sudo apt-get install python3-pip -y

python3 -m venv venv 
source venv/bin/activate
pip3 install bottle
pip3 install oauth2client
pip3 install google-api-python-client
pip3 install Beaker
pip3 install boto3
pip3 install httplib2
nohup python3 app.py
exit 1