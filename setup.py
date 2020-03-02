from pathlib import Path
from setuptools import setup, find_packages

# Parse the requirement file
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = requirements_file.read_text().splitlines()

setup(
    name="bid2d",
    description="Affective simon task for body image distortion",
    author="Christopher Gundler",
    author_email="christopher@gundler.de",
    version="0.0.4.1",
    url="https://gundler.de/",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.7",
    install_requires=requirements,
    zip_safe=True,
    entry_points={"console_scripts": ["bid2d=bid2d.__main__:main"]},
)
