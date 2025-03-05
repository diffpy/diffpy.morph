#############################################
diffpy.pdfmorph documentation
#############################################

diffpy.pdfmorph - Tools for manipulating and comparing PDF profiles.

| Software version |release|.
| Last updated |today|.

Introduction
++++++++++++

``PDFmorph`` is a Python package that increases the insight
researchers can obtain from measured atomic pair distribution functions
(PDFs) in a model-independent way. It was designed to help a
researcher answer the question: "Has my material undergone a phase
transition between these two measurements?"

One approach is to compare the two PDFs in a plot and view the
difference curve underneath. However, significant signal can be seen in
the difference curve from benign effects such as thermal expansion (peak
shifts) and increased thermal motion (peak broadening) or a change in
scale due to differences in incident flux, for example. ``PDFmorph`` will
do its best to correct for these benign effects before computing and
plotting the difference curve. One measured PDF (typically that
collected under higher temperature) is identified as the target PDF and
the second PDF is then morphed by "stretching" (changing the r-axis to
simulate a uniform lattice expansion), "smearing" (broadening peaks
through a uniform convolution to simulate increased thermal motion), and
"scaling" (self-explanatory). PDFmorph will vary the amplitude of the
morphing transformations to obtain the best fit between the morphed and
the target PDFs, then plot them on top of each other with the difference
plotted below.

There are also a few other morphing transformations in the program.
If no morphing transformation is specified, ``PDFmorph`` will return just
the plotted PDFs.

Finally, we note that though ``PDFmorph`` should work on other spectra
that are not PDFs, it has not been extensively tested beyond the PDF.

To get started, please download our :download:`user manual  <pdfmorph.pdf>`
or visit the :ref:`quick_start`.

=======
Authors
=======

``PDFmorph`` is developed by members of the Billinge Group at
Columbia University and Brookhaven National Laboratory including
Christopher L. Farrow, Christopher J. Wright, Pavol Juhás, Chia-Hao
(Timothy) Liu, Andrew Yang, and Simon J. L. Billinge.

For a detailed list of contributors see
https://github.com/diffpy/diffpy.pdfmorph/graphs/contributors.

============
Installation
============

See the `README <https://github.com/diffpy/diffpy.pdfmorph#installation>`_
file included with the distribution.

=================
Table of contents
=================
.. toctree::
   :titlesonly:

   quickstart
   license
   release
   Package API <api/diffpy.pdfmorph>

=======
Indices
=======

* :ref:`genindex`
* :ref:`search`
