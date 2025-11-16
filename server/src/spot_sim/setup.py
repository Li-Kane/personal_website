import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'spot_sim'

# Recursively collect all mesh files while preserving directory structure
def get_data_files(source_dir, target_prefix):
    """Recursively collect files from source_dir and map them to target installation paths."""
    data_files = []
    for root, dirs, files in os.walk(source_dir):
        if files:
            # Calculate relative path from source_dir
            rel_path = os.path.relpath(root, source_dir)
            # Build target installation path
            if rel_path == '.':
                target_path = target_prefix
            else:
                target_path = os.path.join(target_prefix, rel_path)
            # Add all files in this directory
            file_paths = [os.path.join(root, f) for f in files]
            data_files.append((target_path, file_paths))
    return data_files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Recursively install all resource files with directory structure preserved
        *get_data_files('resource', os.path.join('share', package_name, 'resources')),
    ],
    install_requires=['setuptools'],
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
            'sim_sub = spot_sim.sim_sub:main',
        ],
    },
)
