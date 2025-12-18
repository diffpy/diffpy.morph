=============
Release notes
=============

.. current developments

0.3.0
=====

**Added:**

* Tutorials for wrapping PDFgetx3 and PyFai with funcxy.
* morphfuncx added: apply a function to the grid of your morphed function; this function should maintain the monotonic increasing nature of the grid
* morphfuncxy added: apply a general function which can modify both the ordinate and abscissa; useful when applying fourier transform or integration functions
* There is now an option to save the difference curve. This is computed on the common interval between the two curves.
* Raise ``ValueError`` if the number of shared grid points between morphed and target functions is less than the number of parameters.
* Enable ``diffpy.morph`` to detect extrapolation.
* Warnings added to `squeeze` morph if the squeeze causes the grid to become non-monotonic.

**Changed:**

* Removed PDF-specific language from all plotting functions.
* The interpolation of the morphed/objective function onto the target function grid is now done at the end of the morphing chain. Prior, it was done before. This change is desirable as the target function grid may be much smaller/larger than that of the objective, but a morph (e.g. stretch) accounts for that difference. Then, we ensure the morph is done before we regrid for comparison.
* Changed tutorial language away from PDF-specific names
* Names of rmin, rmax, rstep renamed to xmin, xmax, xstep
* Removed PDF-specific labels from plotting functions
* Exclude option in morphpy now takes in a list of morphs to exclude rather than excluding a single morph.
* For diffpy.morph developers: both morphpy functions now have shared code in a separate function for easier maintenance.

**Fixed:**

* Tutorial examples for funcxy and pyfai now run properly.
* Docstring for kwargs updated from dict to Any since various input types from kwargs are possible (e.g. a list/tuple for squeeze, a tuple for funcy, a float for smear-pdf). This should remove the warning that inputs are not dicts.
* When transforming from the RDF to PDF in the smear-pdf morph, we incorrectly referenced the target grid zero point, when we should be referencing the morph grid zero point. This would lead to the morph PDF being set to zero on a point corresponding to when the target PDF grid value is zero. The correct behavior is for the morph PDF to be set to zero when the morph PDF grid value is zero. This has been fixed.
* All morph inputs are now outputted for multiple morphs/targets.
* Docstrings updated for better clarity.
* MorphRGrid can now handle grids denser than 1e-08. Previously, it was possible that multiple points on the intersection range could be excluded.
* Only give user extrapolation warning after refinement.

**Security:**

* Removed subprocess calls in test functions.


0.2.0
=====

**Added:**

* Added a tutorial for MorphFuncy
* Functionality for refining lists and dictionaries
* Add docformatter config to pyproject.toml
* Python interfacing to call PDFmorph
* Returns dictionary of morph metrics (dict) and the r, gr pair for plotting or further manipulation
* General morph function that applies a user-supplied Python function to the y-coordinates of morph data
* Spelling check via Codespell in pre-commit
* Coverage report in each PR
* Added tutorial for MorphSqueeze and MorphFuncy
* Polynomial squeeze of x-axis of morphed data
* --multiple-morphs: morph multiple files against a single target
* New --smear option applies the smear morph directly to the function (without transforming to RDF).
* Support for python 3.13
* manual information is added into online docs.
* Option to set tolerance for the morph refinement (default 1e-08).
* Squeeze morph now added to CLI.
* Error thrown when squeeze morph given improper inputs.
* Shifting morph for vertical and horizontal shifts.

**Changed:**

* Paths to diffpy.utils.parsers functions made explicitly to the file level.
* Changed docstrings location for MorphFuncy and MorphSqueeze
* Typo fixes in documentation.
* Tutorial documentation files split into three sections.
* --multiple changed to --multiple-targets for clarity
* Former --smear option renamed to --smear-pdf (converts PDF to RDF before applying the smear morph).
* Renamed PDFmorph to diffpy.morph
* Stretch disabled when squeeze is above polynomial order 0.
* Horizontal shift morph disabled when squeeze is enabled.
* Squeeze morph now removes duplicate/repeated and trailing commas before parsing.
* Swap colors for morph and target. Morph is now blue and target red.

**Fixed:**

* add temperature field to tutorial/additionalData.
* Multiple morphs/targets used to break given multiple subdirectories.
* reduce the line width limit to 79
* Support ``scikit-package`` Level 5 standard (https://scikit-package.github.io/scikit-package/).
* import `loadData` and `deserialize_data` directly to integrate with `diffpy.utils(3.6.0)`

**Removed:**

* diffpy.morph manual removed.
* Support for python 3.10
* manual.


0.1.3
=====

**Added:**

* Add GitHub action to build wheel, release, upload.
* Add issue and bug report templates.

**Changed:**

* README file installation instructions updated.

**Fixed:**

* Mathematical error in manual


0.1.2
=====

**Changed:**

* downgraded matplotlib requirement to matplotlib-base
* updated imports of bg-mpl-stylesheets for latest release of that code



0.1.1
=====



0.1.1
=====

**Fixed:**

* README title so that it is valid syntax for uploading to PyPi



0.1.0
=====

**Added:**

* Add ability to perform multiple morphs in one call using --multiple.
  * A FILE is morphed against every file in a given DIRECTORY.
  * Can sort PDFs by some field parameter in the header using --sort-by.
  * Can also find the field from some serialized metadata file using --serial-file.
* pdfmorph python function call, which reproduce the application

**Changed:**

* Can now use --verbose tag to limit amount of header information



v0.0.1
====================

**Changed:**

* Fixed rever GH address
