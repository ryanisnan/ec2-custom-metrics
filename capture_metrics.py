import psutil
import requests
import os
import boto3
import argparse
import platform


try:
    response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document', timeout=5)
    AWS_REGION = response.json().get('region')
except:
    raise Exception('Could not fetch the AWS region from AWS')


class Metric(object):
    metric_name = "metric_name"
    metric_unit = "Your Unit"

    @classmethod
    def capture(cls, namespace, value, dimensions):
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
    def get_metric_value(cls):
        raise NotImplementedError


class MaxDiskUsedMetric(Metric):
    metric_name = "disk_used_percent"
    metric_unit = "Percent"

    @classmethod
    def get_metric_value(cls):
        # TODO: Add logging

        # Partitions on the disk
        partitions = psutil.disk_partitions()

        # TODO: Add functionality driven by environment vars or other config to ignore certain partitions
        FSTYPES_TO_IGNORE = ["squashfs"]

        # Keep a list of percentages full by each partition
        pcts = []

        # Measure the available space on each partition
        for partition in partitions:
            if partition.fstype in FSTYPES_TO_IGNORE:
                continue
            
            stat = os.statvfs(partition.mountpoint)
            val = (1 - stat.f_bfree / float(stat.f_blocks)) * 100
            pcts.append(val)
        
        pcts.sort(reverse=True)

        try:
            max_pct = pcts[0]
        except:
            max_pct = None

        return max_pct


class MaxMemoryUsedMetric(Metric):
    metric_name = "mem_used_percent"
    metric_unit = "Percent"

    @classmethod
    def get_metric_value(cls):
        # TODO: Add logging
        stats = psutil.virtual_memory()
        max_pct = stats.percent

        return max_pct


class CPUUsedMetric(Metric):
    metric_name = "cpu_used_percent"
    metric_unit = "Percent"

    @classmethod
    def get_metric_value(cls):
        # TODO: Add logging
        return psutil.cpu_percent()


def get_ec2_instance_id():
    # Return the current EC2 instance ID
    # TODO: Add some sort of file cache so we don't need to ask EC2 all the time
    try:
        return requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    except requests.exceptions.RequestException:
        raise Exception('Failed fetching EC2 instance ID')


def get_hostname():
    return platform.node()


def get_ec2_instance_tags(ec2_instance_id):
    # Return a dict of tags and values for the current EC2 instance
    # TODO: Add some sort of file cache so we don't need to ask EC2 all the time
    ec2 = boto3.client('ec2', region_name=AWS_REGION)
    raw_tags = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values':[ec2_instance_id]}]).get('Tags', [])

    tags = {}
    for raw_tag in raw_tags:
        tags[raw_tag['Key']] = raw_tag['Value']

    return tags


def build_dimensions_from_tags(tags_to_include, tags):
    dimensions = []

    if not tags_to_include:
        return dimensions

    for tag_to_include in tags_to_include.split(','):
        tag_to_include = tag_to_include.strip()

        if not tag_to_include:
            continue

        dimensions.append({
            'Name': tag_to_include,
            'Value': tags[tag_to_include]
        })

    return dimensions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture and push custom cloudwatch metrics')
    parser.add_argument('-n', '--namespace', dest='namespace', required=True, action='store', help='The namespace to log these metrics under')
    parser.add_argument('-d', '--disk-used', dest='disk_used', action='store_true', help='Capture the highest usage level of all disks in use by this machine')
    parser.add_argument('-m', '--memory-used', dest='memory_used', action='store_true', help='Capture the % of memory used by the machine')
    parser.add_argument('-m', '--cpu-used', dest='cpu_used', action='store_true', help='Capture the % of cpu used by the machine')
    parser.add_argument('--tags', dest='tags_to_include', action='store', help='The tags to include in the metrics for dimensions')
    parser.add_argument('--include-hostname', dest='include_hostname', action='store_true', help='Add the hostname as a dimension')
    args = parser.parse_args()

    metrics = []

    if args.disk_used:
        metrics.append(MaxDiskUsedMetric)

    if args.memory_used:
        metrics.append(MaxMemoryUsedMetric)

    ec2_instance_id = get_ec2_instance_id()
    hostname = get_hostname()
    tags = get_ec2_instance_tags(ec2_instance_id)

    dimensions = build_dimensions_from_tags(args.tags_to_include, tags)

    if args.include_hostname:
        dimensions = dimensions + [{
            'Name': 'Host',
            'Value': hostname
        }]

    for metric in metrics:
        value = metric.get_metric_value()

        metric.capture(
            namespace=args.namespace,
            value=value,
            dimensions=dimensions,
        )