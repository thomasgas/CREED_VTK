from setuptools import setup, find_packages

setup(name='CREED_VTK',
      version=1.0,
      description='VTK rendering library for CTA',
      install_requires=[
          'vtk',
          'numpy',
          'astropy'
      ],
      packages=find_packages(),
      tests_require=['pytest'],
      author='Thomas Gasparetto',
      author_email='thomas.gasparetto@ts.infn.it',
      license='MIT',
      url='https://github.com/thomasgas/CREED_VTK',
      long_description='',
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Graphics :: 3D Rendering',
          'Topic :: Scientific/Engineering :: Astronomy',
      ]
      )
