import boto3
import time
import subprocess
import paramiko

subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

#read credentials then get access key id and secret access key
f = open('credentials.csv','r')
f.readline()
line = f.readline()
comma_separated = line.split(',')
aws_access_key_id = comma_separated[0].strip()
aws_secret_access_key = comma_separated[1].strip()

#create client connected to us-east-1
client = boto3.client('ec2', region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

#create key pair if not already made one
key_pair_name = 'test_key_pair'
try:
	key_pair = client.create_key_pair(KeyName='test_key_pair',KeyFormat='pem')
	f = open('test_key_pair.pem', 'w')
	f.write(key_pair['KeyMaterial'])
except Exception as exception:
		print("Exception: ", exception)

#create security group if not already made one 
try:
	security_group = client.create_security_group(Description='authorizations_for_project', GroupName='ece326_Group_15')
	
except Exception as exception:
		print("Exception: ", exception)

#authoeize ports for various purposes for the security group
try:
	client.authorize_security_group_ingress(GroupId='sg-0d57f8fed530d50ce', GroupName='ece326_Group_15',IpPermissions=[{'IpProtocol': 'ICMP', 'FromPort': -1, 'ToPort': -1, 'IpRanges': [{'CidrIp':'0.0.0.0/0'}]},
																													   {'IpProtocol': 'TCP',  'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp':'0.0.0.0/0'}]},
																													   {'IpProtocol': 'TCP',  'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp':'0.0.0.0/0'}]}])
except Exception as exception:
		print("Exception: ", exception)

instance = 0
instanceId = ''
instanceIpAddress = ''
created = False
if len(client.describe_instances(Filters=[{ "Name": "tag:Name", "Values": ["WebServer01"] },
        								  { "Name": "instance-state-name", "Values": ["running"] }])['Reservations']) == 0:
	instances = client.run_instances(ImageId='ami-0866a3c8686eaeeba',
		KeyName=key_pair_name,
		SecurityGroups=['ece326_Group_15'],
		InstanceType='t2.micro',
		MinCount = 1,
		MaxCount = 1)
	print("Waiting for public ip address")
	#wait for public ip address to be assigned
	for i in range(0,15):
		time.sleep(1)
	#get instance id and set true a flag that will tell us to get the ip address
	created = True
	instance = instances['Instances'][0]
	instanceId = instance['InstanceId']

#waits until running before finishing
response = client.describe_instance_status(InstanceIds=[instanceId], IncludeAllInstances=True) 
#get ip address of new instance
if created == True:
	instances = client.describe_instances(InstanceIds=[instanceId])
	instanceIpAddress = instances['Reservations'][0]['Instances'][0]['PublicIpAddress']
while len(response['InstanceStatuses']) == 0:
	time.sleep(1)
print("Waiting for instance to run")
while response['InstanceStatuses'][0]['InstanceState']['Name'] == 'pending':
	time.sleep(1)
	response = client.describe_instance_status(InstanceIds=[instanceId], IncludeAllInstances=True)

print("Instance is running")

# waiting since you can't immediately SSH into the ec2 instance
print("Waiting for instance to stabilize")
for i in range(0,30):
	time.sleep(1)

#using paramiko to connect to the ec2 instance and automatically add new host key
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

privkey = paramiko.RSAKey.from_private_key_file('./test_key_pair.pem')

#make 3 attempts to connect with a 10 second delay between each attempt
for i in range(3):
	try:
		print('SSH into the instance: {}'.format(instanceIpAddress))
		ssh.connect(hostname=instanceIpAddress,
					username='ubuntu', pkey=privkey, port=22)
		print("SSH'd into the instance")
	except Exception as e:
		print(e)
		time.sleep(10)
	else:
		break

#once connected use sftp to copy all files and directories to the ec2 instance
ftp_client=ssh.open_sftp()

ftp_client.put('app.py','app.py')
ftp_client.put('database.db', 'database.db')
ftp_client.put('client_secret.json', 'client_secret.json')
ftp_client.mkdir('views')
ftp_client.put('views/query.tpl', 'views/query.tpl')
ftp_client.put('views/results.tpl', 'views/results.tpl')
ftp_client.mkdir('views/static')
ftp_client.mkdir('views/static/assets')
ftp_client.mkdir('views/static/css')
ftp_client.put('views/static/assets/logo.png', 'views/static/assets/logo.png')
ftp_client.put('views/static/css/style.css', 'views/static/css/style.css')
ftp_client.put('instanceSetup.sh', 'instanceSetup.sh')
ftp_client.close()

#print results first
print("Search engine running on http://%s:8080 with instance id: %s" % (instanceIpAddress, instanceId))

#instanceSetup.sh will also run app.py after installing all python dependencies
#however there is a 1 minute delay roughly and it will take time to see the site run after running this script
(stdin, stdout, stderr) = ssh.exec_command('chmod +rwx instanceSetup.sh')
stdout.read()
stderr.read()
(stdin, stdout, stderr) = ssh.exec_command('~/instanceSetup.sh')
print(stdout.read())
print(stderr.read())

ssh.close()