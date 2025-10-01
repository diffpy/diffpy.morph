.. _funcxy:

Using funcxy with Commonly-Used Diffraction Software
####################################################
The general xy morph ``funcxy`` can be used to tune parameters
of many popular diffraction software functions.

Below, we give templates for how one can use ``funcxy``
with `PDFgetx3 <https://www.diffpy.org/products/pdfgetx.html>`_
and `PyFai <https://pyfai.readthedocs.io/en/stable/>`_.

Getting a Better PDF with PDFgetx3
==================================
In PDFgetx3, the ``PDFGetter`` takes in a 1D diffraction
pattern I(Q) and returns a PDF G(r).

There are many parameters you can specify, such as
  - ``qmin``: Lower Q-cutoff for the Fourier transform giving the PDF
  - ``qmax``: Upper Q-cutoff for the Fourier transform giving the PDF
  - ``qmaxinst``: Upper Q-boundary for meaningful signal
  - ``rpoly``: Approximately the low-r bound of meaningful G(r) values

Furthermore, you can supply a background file ``backgroundfile``
and subtract a scaled version of the background file by the
scaling factor ``bgscale``.

We will showcase an example of how one would refine over the
``PDFGetter`` parameters using ``funcxy`` to obtain a PDF.
.. code-block::

    from diffpy.pdfgetx.pdfgetter import PDFGetter
    from diffpy.morph.morphpy import morph_arrays
    from diffpy.utils.parsers.loaddata import loadData




Performing Detector Calibration with PyFai
==========================================
