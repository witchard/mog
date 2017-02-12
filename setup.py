from setuptools import setup
setup(
  name = 'mog',
  packages = ['mog'],
  version = '0.1',
  description = 'A different take on the UNIX tool cat',
  install_requires = ['mdv', 'pygments'],
  author = 'witchard',
  author_email = 'witchard@hotmail.co.uk',
  url = 'https://github.com/witchard/mog',
  download_url = 'https://github.com/witchard/mog/tarball/0.1',
  keywords = ['terminal', 'highlighting', 'cat'],
  classifiers = [],
  entry_points = {'console_scripts': ['mog = mog:main']}
)

# Thanks to this guide: http://peterdowns.com/posts/first-time-with-pypi.html
