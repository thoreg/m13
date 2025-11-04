"""Handles for file uploads live here."""

import os


def handle_uploaded_file(upload_target_path, file):
    """Handle for single uploaded file."""
    path = os.path.join(upload_target_path, file.name)
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path
