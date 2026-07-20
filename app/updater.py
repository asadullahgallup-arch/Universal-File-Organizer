"""GitHub Release update checks for the desktop application."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPOSITORY = "asadullahgallup-arch/Universal-File-Organizer"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


class UpdateChecker:
    def check(self, installed_version):
        request = Request(
            LATEST_RELEASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Universal-File-Organizer",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                release = json.load(response)
        except HTTPError as error:
            if error.code == 404:
                return {"available": False, "reason": "No published GitHub Release is available yet."}
            raise RuntimeError(f"GitHub returned HTTP {error.code}.") from error
        except URLError as error:
            raise RuntimeError(
                f"Could not connect to GitHub.\n\nReason: {repr(error.reason)}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                f"{type(error).__name__}: {error}"
            ) from error

        latest_version = release.get("tag_name", "").lstrip("vV")
        if not latest_version:
            raise RuntimeError("The latest GitHub Release does not have a version tag.")

        download_url = release.get("html_url")
        assets = release.get("assets", [])
        installer = next(
            (asset for asset in assets if asset.get("name", "").lower().endswith("_setup.exe")),
            None,
        )
        archive = next(
            (asset for asset in assets if asset.get("name", "").lower().endswith(".zip")),
            None,
        )
        selected_asset = installer or archive
        if selected_asset:
            download_url = selected_asset.get("browser_download_url", download_url)

        return {
            "available": self._is_newer(latest_version, installed_version),
            "latest_version": latest_version,
            "download_url": download_url,
            "notes": release.get("body") or "No release notes provided.",
        }

    @staticmethod
    def _is_newer(latest, installed):
        def parts(version):
            values = []
            for value in version.split("."):
                digits = "".join(character for character in value if character.isdigit())
                values.append(int(digits) if digits else 0)
            return tuple((values + [0, 0, 0])[:3])
        return parts(latest) > parts(installed)
