import unittest
import histogram
import numpy as np


class TestHistogram(unittest.TestCase):
    def test_bin_edges(self):
        """
        Verify histogram creation with bin edges only.
        """
        bin_edges = [-0.5, 0.5, 1.5]
        hist = histogram.Histogram(bin_edges=bin_edges)
        self.assertEqual(2, hist.number_of_bins())
        self.assertEqual(bin_edges, hist.bin_edges)

    def test_bin_limits(self):
        """
        Verify histogram creation with bin limits only.
        """
        bin_edges = [-0.5, 0.5, 1.5]
        hist = histogram.Histogram(nbins=2, xmin=-0.5, xmax=1.5)
        self.assertEqual(2, hist.number_of_bins())
        self.assertEqual(bin_edges, hist.bin_edges)

    def test_bin_both(self):
        """
        Verify histogram creation with bin limits and 
        bin edges.
        """
        bin_edges = [-0.5, 0.5, 1.5]
        hist = histogram.Histogram(nbins=10, xmin=22.5, xmax=35.5,
                                   bin_edges=bin_edges)
        self.assertEqual(2, hist.number_of_bins())
        self.assertEqual(bin_edges, hist.bin_edges)

    def test_no_bins(self):
        """
        Create a histogram with no bins.
        """
        self.assertRaises(ValueError, histogram.Histogram)

    def test_normal_use(self):
        """
        Add some entries and check the bin contents.
        """
        hist = histogram.Histogram(10, 0.5, 10.5)
        expected_contents = [0.] * 12
        normalised = [1./12] * 12
        for i in range(0, 12):
            weight = 0.5
            hist.count(i, weight)
            expected_contents[i] += weight
        self.assertEqual(expected_contents, hist.bin_contents)
        self.assertEqual(normalised, hist.norm_contents)


if __name__ == "__main__":
    unittest.main()
