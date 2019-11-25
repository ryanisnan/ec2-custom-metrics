# ec2-custom-metrics

This script exists because AWS doesn't make it super easy to get some metrics about EC2 instances, even with tools like the modern CloudWatch Agent.

In particular, this script adds support for reporting the % of space used by the highest volume associated with a given instance.

# Usage

Clone this repository:

`git clone git@github.com:ryanisnan/ec2-custom-metrics.git`

Install the requirements:

`pip install psutil requests boto3`

Set it on a cron:

`*/5 * * * * AWS_DEFAULT_REGION=us-west-1 python capture_metrics.py`

# Todo

- Make requirements not installed in a really stupid way
- Add a release .tar or .zip
- Make namepsace configurable
- Make metrics to capture configurable
- Add memory usage metric
- Remove region from the env vars