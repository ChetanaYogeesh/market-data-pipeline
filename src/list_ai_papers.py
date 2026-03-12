import os

import pyalex
from pyalex import Works


def main() -> None:
    api_key = os.getenv("OPENALEX_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Please set the OPENALEX_API_KEY environment variable before running this script."
        )

    pyalex.config.api_key = api_key

    # Search for AI-related works and fetch 5 of them
    works = Works().search_filter(title="artificial intelligence").get(per_page=5)

    for idx, work in enumerate(works, start=1):
        title = work.get("title") or work.get("display_name") or "<no title>"
        print(f"{idx}. {title}")


if __name__ == "__main__":
    main()

