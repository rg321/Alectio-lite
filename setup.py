import setuptools


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements("./requirements.txt")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alectiolite",
    version="0.0.1",
    author="Alectio",
    author_email="arun.ram@alectio.com",
    description="Alectio Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alectio/flexible-SDK",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6.10",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=install_reqs,
    python_requires=">=3.6",
)
