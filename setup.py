import setuptools

with open("README.md", "r" , encoding ="utf-8") as fh:
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
    install_requires=["requests>=2", "aiohttp", "gql", "opencv-python", "asyncio", "aiogqlc", "envyaml","yacs"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6.10',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6',
    )
