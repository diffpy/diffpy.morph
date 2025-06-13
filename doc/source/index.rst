#######
diffpy.morph documentation
#######

``diffpy.morph`` - Tools for manipulating and comparing PDF profiles

| Software version |release|
| Last updated |today|.

Introduction
++++++++++++

``diffpy.morph`` is a Python package that increases the insight
researchers can obtain from measured atomic pair distribution functions
(PDFs) in a model-independent way. It was designed to help a
researcher answer the question: "Has my material undergone a phase
transition between these two measurements?"

One approach is to compare the two PDFs in a plot and view the
difference curve underneath. However, significant signal can be seen in
the difference curve from benign effects such as thermal expansion (peak
shifts) and increased thermal motion (peak broadening) or a change in
scale due to differences in incident flux, for example. ``diffpy.morph`` will
do its best to correct for these benign effects before computing and
plotting the difference curve. One measured PDF (typically that
collected under higher temperature) is identified as the target PDF and
the second PDF is then morphed by "stretching" (changing the r-axis to
simulate a uniform lattice expansion), "smearing" (broadening peaks
through a uniform convolution to simulate increased thermal motion), and
"scaling" (self-explanatory). ``diffpy.morph`` will vary the amplitude of the
morphing transformations to obtain the best fit between the morphed and
the target PDFs, then plot them on top of each other with the difference
plotted below.

There are also a few other morphing transformations in the program.
If no morphing transformation is specified, ``diffpy.morph`` will return just
the plotted PDFs.

Finally, we note that though ``diffpy.morph`` should work on other spectra
that are not PDFs, it has not been extensively tested beyond the PDF.

To get started, please visit the :ref:`quick_start`.

=======
Authors
=======

``diffpy.morph`` is developed by members of the Billinge Group at
Columbia University and Brookhaven National Laboratory including
Christopher L. Farrow, Christopher J. Wright, Pavol Juhás, Chia-Hao
(Timothy) Liu, Andrew Yang, and Simon J. L. Billinge.
For a detailed list of contributors see
https://github.com/diffpy/diffpy.morph/graphs/contributors.

============
Installation
============

See the `README <https://github.com/diffpy/diffpy.morph#installation>`_
file included with the distribution.

================
Acknowledgements
================

``diffpy.morph`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.

=================
Table of contents
=================
.. toctree::
   :titlesonly:

   quickstart
   license
   release
   Package API <api/diffpy.morph>

=======
Indices
=======

* :ref:`genindex`
* :ref:`search`
