"""A TCP load-balancer that create backend EC2 instances on-demand.

Usage:
  forward-connection <instance-id> <lock-file> <backend-port>
"""
import boto3
import docopt
import dotenv
import os
import sys
import time
import fcntl
import logging
import subprocess
import signal
import socket
from main import __version__

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
ec2 = boto3.resource('ec2')

def test_socket(hostname, port):
    try:
        with socket.create_connection((hostname, port), 1.0) as sock:
            return True
    except socket.timeout:
        return False
    except ConnectionRefusedError:
        return False

def main():
    args = docopt.docopt(__doc__, version=__version__)

    instance_id = args["<instance-id>"]
    lock_file_name = args["<lock-file>"]
    backend_port = int(args["<backend-port>"])

    instance = ec2.Instance(instance_id)

    with open(lock_file_name, "w") as lock_file:
        sys.stderr.write(f"Waiting for shared lock on '{lock_file_name}'...\n");
        sys.stderr.flush()
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
        sys.stderr.write(f"Obtained lock on '{lock_file_name}'\n")
        sys.stderr.flush()

        ip_address = instance.private_ip_address

        while test_socket(ip_address, backend_port) is False:
            sys.stderr.write(f"Waiting for port {backend_port} on instance {instance_id} ({ip_address})...\n")
            sys.stderr.flush()
            time.sleep(1)

        sys.stderr.write(f"Connection worked, instance {instance_id} is now running\n")
        sys.stderr.flush()

        proc = subprocess.run(["nc", "--", ip_address, str(backend_port)])
        status = proc.returncode
        sys.stderr.write(f"nc exited with status code {status}\n")
        sys.stderr.flush()

        # This cooldown period is useful since often another connection will
        # connection will be made not long after this one has finished. Having
        # this here will keep the instance running for a little longer if this
        # is the case.
        # 
        # 60 seconds was choosen because of the 60 second minimum billing on
        # instances billed 'per-second' on AWS. This means that in the case of a
        # single short-lived connection, we make sure we use the full 60 seconds
        # worth of time that we already paid for to wait for new connections.
        sys.stderr.write("Starting 60 second cooldown...\n")
        sys.stderr.flush()
        time.sleep(60)
        sys.stderr.write("Cooldown finished, shutting down...\n")
        sys.stderr.flush()


        exit(status)


if __name__ == "__main__":
    main()
