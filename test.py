import boto3

ec = boto3.client('ec2', region_name='us-west-2')
elb = boto3.client('elbv2', region_name='us-west-2')

def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:Automated', 'Values': ['HA']},
            { 'Name': 'instance-state-name','Values': ['running'], }
        ]).get('Reservations', [])

    instances = sum(
        [[i for i in r['Instances']]
            for r in reservations], [])

    for instance in instances:

        try:
            stack_tag = [t.get('Value') for t in instance['Tags'] if t['Key'] == 'aws:cloudformation:stack-name'][0]
        except IndexError:
            stack_tag = [t.get('Value') for t in instance['Tags'] if t['Key'] == 'Stack'][0]

        target_groups = elb.describe_target_groups() 
        target_group = [tg['TargetGroupArn'] for tg in target_groups['TargetGroups'] if stack_tag[:3] in tg['TargetGroupArn']]    

        elb.register_targets(
            TargetGroupArn=target_group[0],
            Targets=[
                {
                    'Id' : instance['InstanceId']
                }
            ]
        )









