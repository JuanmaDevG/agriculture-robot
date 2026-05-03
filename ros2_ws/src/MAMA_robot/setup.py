from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'MAMA_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf')),
        ('share/' + package_name, glob('launch/*.py')),
        (os.path.join('share', package_name, 'meshes'), glob(os.path.join('MAMA_robot', 'meshes', '*.stl'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan-docker',
    maintainer_email='juan-docker@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
