**Added:**

* <news item>

**Changed:**

* The interpolation of the morphed/objective function onto the target function grid is now done at the end of the morphing chain. Prior, it was done before. This change is desirable as the target function grid may be much smaller/larger than that of the objective, but a morph (e.g. stretch) accounts for that difference. Then, we ensure the morph is done before we regrid for comparison.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
