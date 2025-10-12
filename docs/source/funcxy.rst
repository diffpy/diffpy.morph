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

Let's say you have a measured I(Q) with Q in angstroms of
glass (composition SiO2) named ``sample.chi`` taken on a
kapton background. We want to match a target calculated PDF G(r)
stored in a file named ``target.cgr``.
Let's also say we have a measured I(Q) of the
kapton background ``background.chi``.

.. code-block:: python

     from diffpy.pdfgetx.pdfgetter import PDFGetter
     from diffpy.morph.morphpy import morph_arrays
     from diffpy.utils.parsers.loaddata import loadData

     pg = PDFGetter()

     backgroundfile = "background.chi"
     composition = "SiO2"


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

     morph_info, morphed_gr = morph_arrays(
                                     sample_iq, target_gr,
                                     funcxy=(wrap, params_to_morph)
                                 )

You can now plot ``morphed_gr`` against your ``target_gr`` to see
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
Our azimuthally integrated ``sample.chi`` looks a bit off.
Before this measurement, you measured an amazing
I(Q) pattern ``target.chi`` with a perfectly calibrated
sample-to-detector distance and beam center.
We will use morphing to try to match the integration of
the 2D pattern to the target 1D function.

For the integration, we will need some information, such as
the wavelength of the beam,
the size of each pixel in the 2D image
(``pixel1`` is the horizontal length in meters and
``pixel2`` is the vertical length in meters),
and a guess of the beam center.
This information can be found on the
`PyFai documentation <https://pyfai.readthedocs.io/en/stable/usage/cookbook/integration_with_python.html>`_.
For our example, let's say we have a ``1024``x``1024`` pixel image
where each pixel is a ``100`` micron by ``100`` micron region, and
our wavelength was ``1.11`` angstroms.

.. code-block:: python

     import numpy as np
     import pyFAI.integrator.azimuthal as pyfai
     import pyFAI.detectors as pfd
     from diffpy.morph.morphpy import morph_arrays
     from diffpy.utils.parsers.loaddata import loadData

     pattern_2d = np.load("diffraction_image.npy")
     wavelength = 0.1110e-9  # in m
     pixel1 = 1e-4  # in m
     pixel2 = 1e-4  # in m
     cent_x = 511   # in number of pixels
     cent_y = 511   # in number of pixels

     ai = pyfai.AzimuthalIntegrator()
     ai.wavelength = wavelength
     detector = pfd.Detector()
     detector.max_shape = pattern_2d.shape


     def wrap(x, y, sample_to_detector_dist, cent_offset_x, cent_offset_y):
         detector.pixel1 = pixel1
         detector.pixel2 = pixel2
         ai.detector = detector

         ai.setFit2D(
             directDist=sample_to_detector_dist,
             centerX=cent_x+cent_offset_x,
             centerY=cent_y+cent_offset_y
         )

         return ai.integrate1d_ng(
                 pattern_2d,
                 npt=1000, unit="q_A^-1",
                 method="mean"
             )


     params_to_morph = {
         "sample_to_detector_dist": 60,  # in mm
         "cent_offset_x": 0,  # in number of pixels
         "cent_offset_y": 0  # in number of pixels
     }

     sample_chi = loadData("sample.chi")
     target_chi = loadData("target.chi")

     morph_info, morphed_chi = morph_arrays(
                                     sample_chi, target_chi,
                                     funcxy=(wrap, params_to_morph)
                                 )

You can now plot ``morphed_chi`` against your ``target_chi``
to see if the refinement has helped in the calibration!
To see the calibrated values, you can print out ``morph_info``.

If you would like to morph over other PyFai parameters
(e.g. ``rot1``, ``tilt``, ``wavelength``),
you can adjust the wrapper function ``wrap`` to take in
these parameters.
