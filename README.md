# ec2-custom-metrics

This script exists because AWS doesn't make it super easy to get some metrics about EC2 instances, even with tools like the modern CloudWatch Agent.

In particular, this script adds support for reporting the % of space used by the highest volume associated with a given instance.

# Usage

Download and install the script:

```
curl -L -o ec2-custom-metrics.tar.gz https://github.com/ryanisnan/ec2-custom-metrics/archive/0.0.1.tar.gz
mkdir ec2-custom-metrics
tar xvzf ec2-custom-metrics.tar.gz --directory ec2-custom-metrics --strip-components 1 && cd ec2-custom-metrics
chmod +x setup.sh && ./setup.sh
```

Test it:

`source venv/bin/activate && python capture_metrics.py --namespace MyNamespace --disk-used`

Set it on a cron:

`*/5 * * * * source /path/to/venv/bin/activate && python /path/to/project/capture_metrics.py --namespace MyNamespace --disk-used`

Assuming everything is set up correctly, metrics will start coming in:

![Example screenshot of cloudwatch metrics of disk_used_percent](screenshot.png)

# Todo

- Add memory usage metric
