import setuptools

setuptools.setup(
    name="flask-geomapper",
    version="3.0.0",
    author="Aarav Borthakur",
    author_email="gadhaguy13@gmail.com",
    description="Visualize Flask request locations cartographically",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gadhagod/flask-geomapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["flask", "pandas", "geopandas", "matplotlib", "requests"]
)
