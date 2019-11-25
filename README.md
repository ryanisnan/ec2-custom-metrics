# ec2-custom-metrics

This script exists because AWS doesn't make it super easy to get some metrics about EC2 instances, even with tools like the modern CloudWatch Agent.

In particular, this script adds support for reporting the % of space used by the highest volume associated with a given instance.

# Usage

Clone this repository:

`git clone git@github.com:ryanisnan/ec2-custom-metrics.git`

Install the requirements:

`virtualenv venv && source venv/bin/activate`
`pip install -r requirements.txt`

Test it:
`python capture_metrics.py --namespace MyNamespace --disk-used`

Set it on a cron:

`*/5 * * * * python capture_metrics.py --namespace MyNamespace --disk-used`

Assuming everything is set up correctly, metrics will start coming in:

![Example screenshot of cloudwatch metrics of disk_used_percent](screenshot.png)

# Todo

- Add a release .tar or .zip
- Add memory usage metric
