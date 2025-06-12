|Icon| |title|_
===============

.. |title| replace:: diffpy.morph
.. _title: https://diffpy.github.io/diffpy.morph

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.morph
        :height: 100px

|PyPI| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.morph/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.morph/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.morph/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.morph

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.morph
        :target: https://anaconda.org/conda-forge/diffpy.morph

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.morph
        :target: https://pypi.org/project/diffpy.morph/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.morph
        :target: https://pypi.org/project/diffpy.morph/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.morph/issues

Python package for manipulating and comparing PDF profiles

``diffpy.morph`` is a Python software package designed to increase the insight
researchers can obtain from measured atomic pair distribution functions
(PDFs) in a model-independent way. The program was designed to help a
researcher answer the question: "Has my material undergone a phase
transition between these two measurements?"

One approach is to compare the two PDFs in a plot and view the difference
curve underneath. However, significant signal can be seen in the
difference curve from benign effects such as thermal expansion (peak
shifts) and increased thermal motion (peak broadening) or a change in
scale due to differences in incident flux, for example. ``diffpy.morph`` will
do its best to correct for these benign effects before computing and
plotting the difference curve. One measured PDF (typically that collected
at higher temperature) is identified as the target PDF and the second
PDF is then morphed by "stretching" (changing the r-axis to simulate a
uniform lattice expansion), "smearing" (broadening peaks through a
uniform convolution to simulate increased thermal motion), and "scaling"
(self-explanatory). ``diffpy.morph`` will vary the amplitude of the morphing
transformations to obtain the best fit between the morphed and the target
PDFs, then plot them on top of each other with the difference plotted
below.

There are also a few other morphing transformations in the program.

Finally, we note that ``diffpy.morph`` should work on other spectra that are not
PDFs, though it has not been extensively tested beyond the PDF.


For more information about the diffpy.morph library, please consult our `online documentation <https://diffpy.github.io/diffpy.morph>`_.

Citation
--------

If you use diffpy.morph in a scientific publication, we would like you to cite this package as

        diffpy.morph Package, https://github.com/diffpy/diffpy.morph

REQUIREMENTS
------------------------------------------------------------------------

``diffpy.morph`` is currently run from the command line, which requires opening
and typing into a terminal window or Windows command prompt. It is
recommended that you consult online resources and become somewhat
familiar before using ``diffpy.morph``.

``diffpy.morph`` can be run with Python 3.10 or higher. It makes use of several third party
libraries that you'll need to run the app and its components.

* `NumPy`              - library for scientific computing with Python
* `matplotlib`         - Python 2D plotting library
* `SciPy`              - library for highly technical Python computing
* `diffpy.utils`       - `shared helper utilities <https://github.com/diffpy/diffpy.utils/>`_ for wx GUI

These dependencies will be installed automatically if you use the conda
installation procedure described below.

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.morph_env`` ::

        conda create -n diffpy.morph_env diffpy.morph
        conda activate diffpy.morph_env

To confirm that the installation was successful, type ::

        python -c "import diffpy.morph; print(diffpy.morph.__version__)"

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.morph_env`` environment, we will also have to install dependencies ::

        pip install -r https://raw.githubusercontent.com/diffpy/diffpy.morph/main/requirements/pip.txt

and then install the package ::

        pip install diffpy.morph

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.morph/>`_. Once installed, ``cd`` into your ``diffpy.morph`` directory
and run the following ::

        pip install .

Getting Started
---------------

You may consult our `online documentation <https://diffpy.github.io/diffpy.morph>`_ for tutorials and API references.

USING diffpy.morph
------------------

For detailed instructions and full tutorial, consult the user manual
on our `website <www.diffpy.org/diffpy.morph/>`.

Once the required software, including ``diffpy.morph`` is all installed, open
up a terminal and check installation has worked properly by running ::

	source activate diffpy.morph_env      #if the environment isn't already active
	diffpy.morph -h			  #get some helpful information
	diffpy.morph --version

If installed correctly, this last command should return the version
of ``diffpy.morph`` that you have installed on your system. To begin using
``diffpy.morph``, run a command like ::

	diffpy.morph <target PDF file> <morphed PDF file>

where both PDFs file are text files which contain PDF data, such as ``.gr``
or ``.cgr`` files that are produced by ``PDFgetX2``, ``PDFgetX3``,
or ``PDFgui``. Though some file extensions other than ``.gr`` or ``.cgr``,
but with the same content structure, have been shown to work with
``diffpy.morph``, it is recommended to stick with ``.gr`` files.

Enjoy!


Support and Contribute
----------------------

`Diffpy user group <https://groups.google.com/g/diffpy-users>`_ is the discussion forum for general questions and discussions about the use of diffpy.morph. Please join the diffpy.morph users community by joining the Google group. The diffpy.morph project welcomes your expertise and enthusiasm!

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.morph/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.morph/pulls>`_. You can also post it to the `Diffpy user group <https://groups.google.com/g/diffpy-users>`_.

Feel free to fork the project and contribute. To install diffpy.morph
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.morph/blob/main/CODE_OF_CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.morph please visit the project `web-page <https://diffpy.github.io/>`_ or email Simon J.L. Billinge group at sb2896@columbia.edu.

Acknowledgements
----------------

``diffpy.morph`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.
