import boto3
from contextlib import closing
import pymysql
import os
from os import environ
import datetime

CONFIG = {
    "Accounts": [
        {
            "role": "arn:aws:iam::123456:role/EC2MonitorTestRole",
            "name": "pshuvalov"
        }
    ]
}


endpoint = environ.get('ENDPOINT')
port = int(environ.get('PORT'))
dbuser = environ.get('DBUSER')
password = environ.get('DBPASSWORD')
database = environ.get('DATABASE', 'ec2monitor')

conn = pymysql.connect(endpoint, port=port, user=dbuser, passwd=password, db=database, connect_timeout=5)

print("Initing MySQL Schema")
with open("%s/schema.sql" % os.path.dirname(os.path.abspath(__file__))) as schema, closing(conn.cursor()) as cursor:
    for stmt in filter(lambda x: len(x.strip()) > 0, schema.read().split(";")):
        cursor.execute(stmt)
conn.commit()

def session_with_role(role_arn, session_name):
    client = boto3.client('sts')
    response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])

def _prepareDate(d):
    print(d, type(d))
    return d.strftime('%Y-%m-%d %H:%M:%S')

def process_account(acc, cursor):
    now = datetime.datetime.now()
    print("Start processing for %s" % acc)
    session = session_with_role(acc['role'], acc['name'])

    for region in session.get_available_regions('ec2'):
        print("Processing region %s" % region)
        ec2 = session.client('ec2', region_name=region)
        response = ec2.describe_instances(Filters=[])
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                lifecycle = instance.get('InstanceLifecycle', 'normal')
                if lifecycle == "spot":
                    continue
                if lifecycle == "scheduled":
                    continue
                assert lifecycle == "normal"
                instance_id = instance['InstanceId']
                platform = instance.get('Platform', 'Linux')
                image_id = instance['ImageId']
                instance_type = instance['InstanceType']
                cpu_core_count = instance['CpuOptions']['CoreCount']
                cpu_threads_per_core = instance['CpuOptions']['ThreadsPerCore']
                state = instance['State']['Name']
                tenancy = instance['Placement']['Tenancy']
                launch_time = instance['LaunchTime']
                print(launch_time)
                print(type(launch_time))
                args = (acc['name'], _prepareDate(now), region, instance_id, platform, image_id, instance_type,
                        int(cpu_core_count), int(cpu_threads_per_core), state, tenancy, _prepareDate(launch_time))
                cursor.execute("""
                INSERT INTO InstanceLog(
                  client, checkTime, region, instanceId, platform, imageId, 
                  instanceType, cpuCoreCount, cpuThreadsPerCore, state, tenancy, launchTime
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, args)
                print(args)
    
def lambda_handler(event, context):
    for acc in CONFIG['Accounts']:
        with closing(conn.cursor()) as cursor:
            process_account(acc, cursor)
        conn.commit()

    return 'Finished'

if __name__ == "__main__":
	lambda_handler(None, None)
