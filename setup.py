#!/usr/bin/env python3
"""Setup script for trading-backtest package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trading-backtest",
    version="0.1.0",
    author="Zruvan",
    description="A Python-based backtesting framework for testing trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zruvan/trading-backtest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "requests>=2.25.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "reportlab>=3.6.0",
        "yfinance>=0.1.70",
        "python-dotenv>=0.19.0",
        "structlog>=21.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.6.0",
            "flake8>=3.9.0",
            "alembic>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trading-backtest=scripts.run_backtest:main",
        ],
    },
)
