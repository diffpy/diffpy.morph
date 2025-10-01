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

Let's say you have a measured I(Q) with Q in angstroms of a lead
nanoparticle (composition PbS) named ``sample.chi`` taken on a
glass background. We want to match a target calculated PDF G(r)
stored in a file named ``target.cgr``.
Let's also say we have a measured I(Q) of the
glass background ``background.chi``.
.. code-block:: python

     from diffpy.pdfgetx.pdfgetter import PDFGetter
     from diffpy.morph.morphpy import morph_arrays
     from diffpy.utils.parsers.loaddata import loadData

     pg = PDFGetter()

     backgroundfile = loadData("background.chi")
     composition = "PbS"


     def wrap(x, y, **kwargs):
         xy_out = pg.__call__(
                         x=x, y=y, dataformat="QA",
                         composition=composition,
                         backgroundfile=backgroundfile,
                         **kwargs
                     )
         r = xy_out[0]
         gr = xy_out[1]
         return (r, gr)


     sample_iq = loadData("sample.chi")
     target_gr = loadData("target.cgr")
     params_to_morph = {
         "bgscale": 1.0,
         "qmin": 0.0, "qmax": 25.0,
         "qmaxinst": 25.0, "rpoly": 0.9
     }

     morph_info, morph_table = morph_arrays(
                                     sample_iq, target_gr,
                                     funcxy=(wrap, params_to_morph)
                                 )


You can now plot ``morph_table`` against your ``target_gr`` to see
how well your morphing refinement of the PDF-getting parameters
as done!
To see what the refined values of the parameters are,
print out ``morph_info``.
You can freely add and remove entries in
``params_to_morph`` to include or not include them as
parameters to refine over.

If you expect to see thermal effect differences between your
measured PDF and ``target_gr``, you can also include
the ``stretch``, ``scale``, and ``smear`` morphs in your
call to ``morph_arrays``.


Performing Detector Calibration with PyFai
==========================================
When performing azimuthal integration, it is important to
ensure your beam center and detector distances are calibrated.
However, it is possible that they have shifted
across measurements. Here, we will use morphing to the rescue!

Let's say we just measured a diffraction pattern stored
as a NumPy object in ``diffraction_image.npy``, but some
of the detector geometries are off.
Before this measurement, you measured an amazing
I(Q) pattern ``target.chi`` with a perfectly calibrated
sample-to-detector distance and beam center.
We will use morphing to try to recalibrate.

.. code-block:: python

     import numpy as np
     import pyFAI.integrator.azimuthal as pyfai
     import pyFAI.detectors as pfd
     from diffpy.morph.morphpy import morph_arrays
     from diffpy.utils.parsers.loaddata import loadData

     pattern_2d = np.load("diffraction_image.npy")
     wavelength = #
     pixel1 = #
     pixel2 = #

     ai = pyfai.AzimuthalIntegrator()
     ai.wavelength = wavelength
     detector = pfd.Detector()
     detector.max_shape = pattern_2d.shape

     def wrap(x, y, sample_to_detector_dist, cent_offset_x, cent_offset_y):
         detector.pixel1 = pixel1
         detector.pixel2 = pixel2


         ai.detector = detector
