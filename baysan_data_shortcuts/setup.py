from setuptools import setup, find_packages

setup(
    author="Baysan | @mebaysan",
    description="I created this package to have an instance about how we can create custom Python packages. Also, I use this package my projects.",
    name="baysan-data-shortcuts",
    version="0.1.0",
    packages=find_packages(
        include=["baysan_data_shortcuts", "baysan_data_shortcuts.*"]
    ),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "lifetimes",
    ],
    python_requires=">=3.8",
)
