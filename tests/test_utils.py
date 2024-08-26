import numpy as np

from src.utils.utils import interpolate_beta_values


class TestUtils:

    def test_interpolate_beta_values(self) -> np.ndarray:
        """
        Function to interpolate the beta values for the years in the years_output list.

        :param years_output: The years for which the beta values need to be interpolated.
        :param betas: The beta values for the years in the years list.
        :param years: The years for which the beta values are known.
        :return: The interpolated beta values for the years_output list.
        """

        years_output = np.linspace(2025, 2100, 76)
        years = np.array([2036, 2035, 2045, 2050])
        betas = np.array([2.2, 2.1, 2.0, 1.9])
        betas = interpolate_beta_values(years_output, betas, years)

        assert isinstance(betas, np.ndarray)
