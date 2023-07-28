from setuptools import setup

setup(
    name='my_program',
    version='1.0.0',
    packages=['your_package_name'],  # Remplacez 'your_package_name' par le nom du package contenant votre programme
    install_requires=[
        'pygame',
        'pygame_widgets',
    ],
    entry_points={
        'console_scripts': [
            'my_program = your_package_name.main:main'  # Remplacez 'your_package_name' par le nom du package contenant votre programme
        ]
    }
)