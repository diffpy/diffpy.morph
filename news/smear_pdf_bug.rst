**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* When transforming from the RDF to PDF in the smear-pdf morph, we incorrectly referenced the target grid zero point, when we should be referencing the morph grid zero point. This would lead to the morph PDF being set to zero on a point corresponding to when the target PDF grid value is zero. The correct behavior is for the morph PDF to be set to zero when the morph PDF grid value is zero. This has been fixed.

**Security:**

* <news item>
