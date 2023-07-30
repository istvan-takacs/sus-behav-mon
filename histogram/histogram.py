class Histogram:
    """
    A class to provide histogram functionality.
    """
    def __init__(self,
                 nbins: int = 0,
                 xmin: float = 0.,
                 xmax: float = 0.,
                 bin_edges: list = []) -> None:
        if not isinstance(bin_edges, list):
            raise TypeError("The bin_edges must be a list.")
        for bin_edge in bin_edges:
            if not isinstance(bin_edge, float):
                raise TypeError("bin_edges must contain floats.")

        if len(bin_edges) > 0:
            self.bin_edges = bin_edges.copy()
            self.bin_edges.sort()
        else:
            self.set_bin_edges(nbins, xmin, xmax)
        self.bin_contents = [0.] * (len(self.bin_edges) + 1)
        self.norm_contents = self.bin_contents.copy()

    def set_bin_edges(self,
                      nbins: int,
                      xmin: float,
                      xmax: float) -> None:
        """
        Set bin edges uniformly from xmin to xmax.
        """

        # In case the histogram definition is not valid.
        if not isinstance(nbins, int):
            raise TypeError("nbins must be an integer.")
        if nbins <= 0:
            raise ValueError("nbins must be a positive integer greater than zero.")
        if not isinstance(xmin, float):
            raise TypeError("xmin must be a float.")
        if not isinstance(xmax, float):
            raise TypeError("xmax must be a float.")
        if xmin >= xmax:
            raise ValueError("xmin must be less than xmax.")

        # Define the bin edges uniformly.
        self.bin_edges = [0.] * (nbins + 1)
        bin_size = float(xmax - xmin)/nbins
        for i in range(nbins):
            self.bin_edges[i] = xmin + bin_size*i
        self.bin_edges[nbins] = xmax

    def number_of_bins(self) -> int:
        """
        A function to return the number of bins in the histogram.
        """
        return len(self.bin_contents) - 2

    def find_bin_index(self, value: float) -> int:
        """
        A function to find the index of the bin given
        an input value.
        """

        # In case the histogram definition is not valid.
        if len(self.bin_edges) == 0:
            raise IndexError("No bin edges have been defined.")
        
        # The value must be a float or something that can 
        # be cast into a float.
        try:
            value = float(value)
        except ValueError:
            raise ValueError("The value must be able to be cast to a float.")
        
        # Underflow bin.
        if value < self.bin_edges[0]:
            return 0

        # Overflow bin.
        if value >= self.bin_edges[-1]:
            return len(self.bin_contents) - 1
        
        # Find the bin.
        n_bins = len(self.bin_contents) - 2
        for i in range(1, n_bins+1):
            if value < self.bin_edges[i]:
                return i

    def __add_entry(self, value: float, weight: float) -> None:
        """
        A function to count a value within the histogram.
        """
        bin_index = self.find_bin_index(value)
        self.bin_contents[bin_index] += weight

    def __normalise(self) -> None:
        """
        A function to create an updated normalised histogram.
        """
        total = sum(self.bin_contents)
        for i in range(len(self.bin_contents)):
            self.norm_contents[i] = self.bin_contents[i]/total
        pass

    def count(self, value: float, weight: float = 1.0) -> None:
        """
        A function to count a value within the histogram,
        using an optional weight.
        """
        if not isinstance(weight, float):
            raise ValueError("The weight must be a float.")
        self.__add_entry(value, weight)
        self.__normalise()
