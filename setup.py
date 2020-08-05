import setuptools
from tcp_scaler import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tcp-scaler-natruiz3553",
    version=__version__,
    author="Nathan Ruiz",
    author_email="natruiz3553@gmail.com",
    description="A TCP load-balancer that create backend EC2 instances on-demand",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/natruiz3555/tcp-scaler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "tcp-scaler=tcp_scaler:main",
            "tcp-scaler-forwarder=tcp_scaler:forwarder"
        ]
    },
    install_requires=[
        "boto3",
        "docopt",
        "python-dotenv"
    ]
)
