from program import normalize

def test_normalize():
    # Test case for an empty list
    assert normalize([]) == [], "Failed on empty list"

    # Test case for a list with negative numbers
    try:
        normalize([1, -1])
        assert False, "Failed to raise an exception on negative numbers"
    except ValueError:
        pass  # Expected outcome, should raise an exception

# Run the tests
test_normalize()

