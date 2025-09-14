"""
CarBot Pro - CrewAI Multi-Agent Automotive Sales System
Professional setup script for installation and distribution
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="carbot-pro",
    version="1.5.0",
    author="Edwin Quintero Alzate",
    author_email="egqa1975@gmail.com",
    description="CrewAI Multi-Agent System for Automotive Sales - Production Ready",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Edwin1719/Car_Agent_CrewAI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["data/*.csv", "*.md"],
    },
    entry_points={
        "console_scripts": [
            "carbot-pro=streamlit_app:main",
        ],
    },
    keywords="crewai, ai-agents, automotive, sales, streamlit, gpt-4",
    project_urls={
        "Bug Reports": "https://github.com/Edwin1719/Car_Agent_CrewAI/issues",
        "Source": "https://github.com/Edwin1719/Car_Agent_CrewAI",
        "Documentation": "https://github.com/Edwin1719/Car_Agent_CrewAI/blob/main/README.md",
    },
)