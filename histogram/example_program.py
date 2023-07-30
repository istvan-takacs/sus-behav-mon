import histogram


if __name__ == "__main__":
    # Define a histogram with bin edges that
    # are hours in the day.
    bin_edges = [
        0.,
        7.,
        12.,
        18.,
        24.
    ]
    hist = histogram.Histogram(bin_edges=bin_edges)

    # Add some times when someone did something.
    hist.count(8)
    hist.count(9)
    hist.count(10)
    hist.count(16)

    # Probabilities for bins, excluding under and overflow.
    # (The first bin is the underflow.  The last bin is the overflow.)
    print(hist.norm_contents[1:-1])

    threshold = 0.1

    # 1am.
    hour = 1
    bin_index = hist.find_bin_index(hour)
    if hist.norm_contents[bin_index] < threshold:
        print(f"Alert! hour={hour}")
    
    # 9am.
    hour = 9
    if hist.norm_contents[hist.find_bin_index(hour)] < threshold:
        print(f"Alert! hour={hour}")
