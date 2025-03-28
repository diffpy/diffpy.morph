import numpy as np
import pytest

from diffpy.morph.morphs.morphsqueeze import MorphSqueeze


class TestMorphSqueeze:
    @pytest.fixture
    def setup(self):
        # Create a sine-wave for testing
        self.x_morph = np.linspace(0, 2 * np.pi, 1000)
        self.y_morph = np.sin(self.x_morph)
        self.x_target = self.x_morph.copy()
        self.y_target = self.y_morph.copy()
        return

    def test_no_squeeze(self, setup):
        """When squeeze is zero, the input should be unchanged."""
        morph = MorphSqueeze()
        morph.squeeze = 0.0

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Verify that the morph output matches the original input
        assert np.allclose(x_morph, self.x_morph)
        assert np.allclose(y_morph, self.y_morph)
        # And the target arrays remain unchanged
        assert np.allclose(x_target, self.x_target)
        assert np.allclose(y_target, self.y_target)

    def test_morph_with_squeeze(self, setup):
        """Test that with a non-zero squeeze,
        x_morph is transformed non-linearly."""
        morph = MorphSqueeze()
        morph.squeeze = 0.7
        x_new, y_new, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Check that target arrays remain unchanged
        assert np.allclose(self.y_target, y_target)

        # For this test, we expect:
        # x_new = x_morph + squeeze_factor * sin(x_morph)
        expected_x = self.x_morph + morph.squeeze * np.sin(self.x_morph)
        expected_y = np.sin(expected_x)

        # Allow for some tolerance because of numerical interpolation if used
        res = sum(np.fabs(expected_y - y_new))
        assert res < 1


if __name__ == "__main__":
    TestMorphSqueeze()
