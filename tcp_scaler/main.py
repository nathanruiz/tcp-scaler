"""A TCP load-balancer that create backend EC2 instances on-demand.

Usage:
  tcp-scaler <instance-id> <lock-file>
"""
import boto3
import docopt
import dotenv
import os
import sys
import time
import fcntl

__version__ = '0.0.1'

dotenv.load_dotenv()
ec2 = boto3.resource('ec2')

def main():
    args = docopt.docopt(__doc__, version=__version__)

    instance_id = args["<instance-id>"]
    lock_file_name = args["<lock-file>"]

    instance = ec2.Instance(instance_id)

    print(f"Started instance manager for {instance_id}")

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
                print("Instance stopped but connections are active, starting...")
                instance.start()
                instance.wait_until_running()
                print("Instance started")
        elif state == "running":
            if not should_be_running:
                print("Instance running with no connections, stopping...")
                instance.stop()
                instance.wait_until_stopped()
                print("Instance stopped")
        elif state == "pending":
            print("Waiting for instance to start...")
            instance.wait_until_running()
            print("Instance started")
        elif state in {"shutting-down", "stopping"}:
            print("Waiting for instance to stop...")
            instance.wait_until_stopped()
            print("Instance stopped")
        elif state == "terminated":
            print("Instance terminated, giving up")
            exit(1)
        else:
            print(f"Unexpected state {state}")

        time.sleep(1)

if __name__ == "__main__":
    main()
