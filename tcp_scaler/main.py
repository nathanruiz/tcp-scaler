"""A TCP load-balancer that create backend EC2 instances on-demand.

Usage:
  tcp-scaler [-v] <instance-id> <lock-file>

Options:
  -v --verbose  Write extra state information to the console
"""
import boto3
import docopt
import dotenv
import fcntl
import logging
import os
import sys
import time
from .__version__ import __version__


logger = logging.getLogger(__name__)

def main():
    dotenv.load_dotenv()
    ec2 = boto3.resource('ec2')

    args = docopt.docopt(__doc__, version=__version__)

    if args["--verbose"]:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(level=level, format="%(message)s")

    instance_id = args["<instance-id>"]
    lock_file_name = args["<lock-file>"]

    instance = ec2.Instance(instance_id)

    logger.info(f"Started instance manager for {instance_id}")

    while True:
        with open(lock_file_name, "w") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
                should_be_running = False
            except OSError:
                should_be_running = True

        instance.reload()
        state = instance.state["Name"]

        if state == "stopped":
            if should_be_running:
                logger.info("Instance stopped but connections are active, starting...")
                instance.start()
                instance.wait_until_running()
                logger.info("Instance started")
        elif state == "running":
            if not should_be_running:
                logger.info("Instance running with no connections, stopping...")
                instance.stop()
                instance.wait_until_stopped()
                logger.info("Instance stopped")
        elif state == "pending":
            logger.info("Waiting for instance to start...")
            instance.wait_until_running()
            logger.info("Instance started")
        elif state in {"shutting-down", "stopping"}:
            logger.info("Waiting for instance to stop...")
            instance.wait_until_stopped()
            logger.info("Instance stopped")
        elif state == "terminated":
            logger.info("Instance terminated, giving up")
            exit(1)
        else:
            logger.info(f"Unexpected state {state}")

        time.sleep(1)

if __name__ == "__main__":
    main()
