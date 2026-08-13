from collections.abc import Iterator
from numpy.typing import NDArray
from typing import Any

def iter_chunks(
    array: NDArray[Any],
    chunk_size: int,
) -> Iterator[tuple[slice, NDArray[Any]]]:
    """Iterate over the first axis of an array in chunks."""
    for start in range(0, array.shape[0], chunk_size):
        end = min(start + chunk_size, array.shape[0])
        slc = slice(start, end)
        yield slc, array[slc]