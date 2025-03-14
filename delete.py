import os
import zipfile
import rarfile

def is_zip_corrupted(filepath):
    """Check if a .cbz (ZIP) file is corrupted."""
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            return zf.testzip() is not None  # If testzip() returns None, the file is fine
    except zipfile.BadZipFile:
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return False  # Do NOT assume corruption on unexpected errors

def is_rar_corrupted(filepath):
    """Check if a .cbr (RAR) file is corrupted."""
    try:
        with rarfile.RarFile(filepath, 'r') as rf:
            rf.testrar()  # If no exception is raised, the file is fine
            return False
    except rarfile.BadRarFile:
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return False  # Do NOT assume corruption on unexpected errors

def delete_corrupted_comics(directory="F:\\Books"):
    """Check and delete only corrupted .cbr and .cbz files, ignoring 0 KB and valid files."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:  # Ignore 0 KB files
            if file.lower().endswith(".cbz"):
                if is_zip_corrupted(filepath):
                    print(f"Deleting corrupted CBZ file: {filepath}")
                    os.remove(filepath)
                else:
                    print(f"CBZ file is valid: {filepath}")
            elif file.lower().endswith(".cbr"):
                if is_rar_corrupted(filepath):
                    print(f"Deleting corrupted CBR file: {filepath}")
                    os.remove(filepath)
                else:
                    print(f"CBR file is valid: {filepath}")

if __name__ == "__main__":
    delete_corrupted_comics()
    print("Scan complete.")
