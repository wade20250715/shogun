from setuptools import setup, find_packages

setup(
    name="shogun-agent",
    version="0.1.0",
    description="将军家老足轻 — 轻量级多Agent文件系统协作调度器",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="wade20250715",
    url="https://github.com/wade20250715/shogun",
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
