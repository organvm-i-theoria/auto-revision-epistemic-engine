from setuptools import setup, find_packages

setup(
    name="auto-revision-epistemic-engine",
    version="4.2.0",
    description="Self-governing orchestration framework with eight phases and four human oversight gates",
    author="Auto-Rev Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "blake3>=0.4.1",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
