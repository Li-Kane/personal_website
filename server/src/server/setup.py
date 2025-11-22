# SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

package_name = 'server'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'websockets',
    ],
    zip_safe=True,
    maintainer='Kane Li',
    maintainer_email='kaneli200456@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'server = server.server:main',
        ],
    },
)
