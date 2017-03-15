from setuptools import setup
setup(
  name = 'mog',
  packages = ['mog'],
  version = '0.6.0',
  description = 'A different take on the UNIX tool cat',
  install_requires = ['pygments'],
  author = 'witchard',
  author_email = 'witchard@hotmail.co.uk',
  url = 'https://github.com/witchard/mog',
  download_url = 'https://github.com/witchard/mog/tarball/0.6.0',
  keywords = ['terminal', 'highlighting', 'cat'],
  classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: MIT License',
      'Operating System :: POSIX',
      'Operating System :: POSIX :: Linux',
      'Operating System :: POSIX :: BSD',
      'Operating System :: MacOS',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Topic :: System',
      'Topic :: Utilities',
  ],
  entry_points = {'console_scripts': ['mog = mog:main']}
)

# DONT FORGET TO CHANGE DOWNLOAD_URL WHEN DOING A RELEASE!
# Thanks to this guide: http://peterdowns.com/posts/first-time-with-pypi.html
# Release with:
#    git tag <version>
#    git push --tags
#    python setup.py sdist upload -r pypi

