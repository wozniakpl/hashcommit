from setuptools import setup, find_packages
from hashcommit.version import VERSION

setup(
    name='hashcommit',
    version=VERSION,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hashcommit = hashcommit.main:main',
        ],
    },
    install_requires=[],
    author='Bartosz Woźniak',
    author_email='bwozniakdev@protonmail.com',
    description='A tool to generate a Git commit with a specific hash part.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wozniakpl/hashcommit',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
