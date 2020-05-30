import setuptools


with open("README.rst", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="entomb",
    version="0.1.0",
    description="File immutability manager",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Sky Christensen",
    author_email="sky@skychristensen.com",
    url="https://github.com/countermeasure/entomb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
    keywords="immutable",
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "entomb=entomb.core:run",
        ],
    },
)
