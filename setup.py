from setuptools import setup, find_packages

setup(
    name='gefplus',
    version='0.0.1',
    description='A desktop application for survival analysis.',
    author='Mattia Neroni, Ph.D, Eng.',
    author_email='mattianeroni@yahoo.it',
    url='https://github.com/mattianeroni/gefplus',
    package_dir = {
        'gefplus': 'gefplus'
    },
    packages=[
        'gefplus'
    ],
    python_requires='>=3.11',
    classifiers=[
        "Development Status :: 3 - Alpha"
    ]
)