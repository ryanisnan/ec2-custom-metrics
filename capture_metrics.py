import psutil
import requests
import os
import boto3
import argparse


try:
    response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document', timeout=5)
    AWS_REGION = response.json().get('region')
except:
    raise Exception('Could not fetch the AWS region from AWS')


class Metric(object):
    metric_name = "metric_name"
    metric_unit = "Your Unit"

    @classmethod
    def capture(cls, namespace):
        value, dimensions = cls.get_metric_value_and_dimensions()
        cls.put_metric_data(namespace, value, dimensions)

    @classmethod
    def put_metric_data(cls, namespace, value, dimensions=None):
        # Demensions defaults to an emtpy list if nothing has been supplied
        dimensions = dimensions or []

        cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)
        cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    'MetricName': cls.metric_name,
                    'Dimensions': dimensions,
                    'Unit': cls.metric_unit,
                    'Value': value
                }
            ],
        )

    @classmethod
    def get_metric_value_and_dimensions(cls):
        raise NotImplementedError

    @classmethod
    def get_ec2_instance_id(cls):
        try:
            return requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
        except requests.exceptions.RequestException:
            raise Exception('Failed fetching EC2 instance ID')


class MaxDiskUsedMetric(Metric):
    metric_name = "disk_used_percent"
    metric_unit = "Percent"

    @classmethod
    def get_metric_value_and_dimensions(cls):
        # TODO: Add logging

        # Partitions on the disk
        partitions = psutil.disk_partitions()

        # TODO: Add functionality driven by environment vars or other config to ignore certain partitions

        # Keep a list of percentages full by each partition
        pcts = []

        # Measure the available space on each partition
        for partition in partitions:
            stat = os.statvfs(partition.mountpoint)
            val = (1 - stat.f_bfree / float(stat.f_blocks)) * 100
            pcts.append(val)
            pcts.sort(reverse=True)

        try:
            max_pct = pcts[0]
        except:
            max_pct = None
        
        dimensions = [{
            'Name': 'InstanceId',
            'Value': cls.get_ec2_instance_id()
        }]

        return (max_pct, dimensions)


class MaxMemoryUsedMetric(Metric):
    metric_name = "mem_used_percent"
    metric_unit = "Percent"

    @classmethod
    def get_metric_value_and_dimensions(cls):
        # TODO: Add logging
        stats = psutil.virtual_memory()
        max_pct = stats.percent
        
        dimensions = [{
            'Name': 'InstanceId',
            'Value': cls.get_ec2_instance_id()
        }]

        return (max_pct, dimensions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture and push custom cloudwatch metrics')
    parser.add_argument('-n', '--namespace', dest='namespace', required=True, action='store', help='The namespace to log these metrics under')
    parser.add_argument('-d', '--disk-used', dest='disk_used', action='store_true', help='Capture the highest usage level of all disks in use by this machine')
    parser.add_argument('-m', '--memory-used', dest='memory_used', action='store_true', help='Capture the % of memory used by the machine')
    args = parser.parse_args()

    metrics = []
    
    if args.disk_used:
        metrics.append(MaxDiskUsedMetric)
    
    if args.memory_used:
        metrics.append(MaxMemoryUsedMetric)

    for metric in metrics:
        metric.capture(namespace=args.namespace)
