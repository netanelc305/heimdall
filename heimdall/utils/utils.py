from pathlib import Path

import requests
from tqdm import tqdm

DEFAULT_CHUNK_SIZE = 1024
DEFAULT_PAGE_SIZE = 4096


def download_file(url: str, output_file: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
    """
    Download a file from a URL in chunks and save it to a specified path.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    output_file : Path
        The path where the downloaded file will be saved.
    chunk_size : int, optional
        The size of each chunk to download (default is DEFAULT_CHUNK_SIZE).

    Returns
    -------
    None
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(output_file, 'wb') as file, tqdm(
            desc=output_file.name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            size_written = file.write(chunk)
            progress_bar.update(size_written)
