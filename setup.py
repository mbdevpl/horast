"""Setup script for horast package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):

    """Package metadata."""

    name = 'horast'
    description = 'human-oriented ast parser/unparser'
    download_url = 'https://github.com/mbdevpl/horast'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Utilities']
    keywords = ['ast', 'parsing', 'unparsing', 'comments']


if __name__ == '__main__':
    Package.setup()
