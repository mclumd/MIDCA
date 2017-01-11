#!/usr/bin/env python

from distutils.core import setup

setup(name='baxter_srv',
      version='1.0',
      description='baxter_srv',
      author='Zohreh A',
      author_email='',
      packages=['baxter_srv', 'baxter_srv.srv'],
      package_dir={"": ".."}
     )

