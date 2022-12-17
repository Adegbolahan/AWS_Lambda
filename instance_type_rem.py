import json
import boto3
import time
client_ec2 = boto3.client('ec2')
paginator = client_ec2.get_paginator('describe_instances')

#get all ec2 list
def get_ec2_list():
    instance_list=[]
    response_iterator = paginator.paginate(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ]
            },
        ],
    )
    for item in response_iterator['Reservations']:
        for instance in item['Instances']:
            try:
                instance_id=instance['InstanceId']
                instance_type=instance['InstanceType']
                keyname=instance['KeyName']
            except KeyError as e:
                instance_id=instance['InstanceId']
                instance_type=instance['InstanceType']
                keyname='-'
                print("Exception detected: ", e)
            finally:
                instance_list.append((instance_id,instance_type,keyname))
    return instance_list

    # [(instance_id,instance_type,keyname),(instance_id,instance_type,keyname),(instance_id,instance_type,keyname),(instance_id,instance_type,keyname)]

#Check instance_type to verify complaince
def complaince_check(result,valid_instance_type):
    complaint_list, non_complaint_list=[],[]
    for item in result:
        if item[1] not in valid_instance_type:
            non_complaint_list.append(item)
        else:
            complaint_list(item)
    return complaint_list,non_complaint_list

#Remediate non-complaint instances by replacing the instance_type
def remediate(rem_list,dry_run,valid_instance_type):
    for item in rem_list:
        stop_instance(item,dry_run)
        if dry_run == 'False':
            time.sleep(30)
            response = client_ec2.modify_instance_attribute(
                InstanceId=item[0],
                InstanceType={
                    'Value': valid_instance_type[0]
                },
            )
            start_instance(item,dry_run)
            print(f"{item[0]}stopped, instance_type replace with {valid_instance_type[0]}")
            print(f{item[0]} restarted!)
        else:
            print(f"{item[0]} will be stopped")
            print("To stop set 'dry_run' to 'False'")

#Stop instance scheduled for remediation
def stop_instance(item,dry_run):
    if dry_run == 'False':
        response = client_ec2.stop_instances(
            InstanceIds=[
                item[0],
            ],
        )

        print(f"{item[0]} has been stopped!")
    else:
        print(f"{item[0]} will be stopped")
        print("To stop set 'dry_run' to 'False'")

#Start instance after remediation
def start_instance(item,dryrun):
    if dry_run == 'False':
        response = client_ec2.start_instances(
            InstanceIds=[
                item[0],
            ],
        )
        print(f"{item[0]} has been started!")
    else:
        print(f"{item[0]} will be started")
        print("To restart instance set 'dry_run' to 'False'")

if __name__ == "__main__":
    dry_run=True
    valid_instance_type=['t2.micro']
    result=get_ec2_list()
    rem_list=complaince_check(result,valid_instance_type)
    remediate(rem_list[1],dry_run,valid_instance_type)