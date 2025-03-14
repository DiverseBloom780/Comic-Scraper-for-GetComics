import os
import zipfile
import rarfile

def is_zip_corrupted(filepath):
    """Check if a .cbz (ZIP) file is corrupted."""
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            return zf.testzip() is not None
    except zipfile.BadZipFile:
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return True
    return False

def is_rar_corrupted(filepath):
    """Check if a .cbr (RAR) file is corrupted."""
    try:
        with rarfile.RarFile(filepath, 'r') as rf:
            rf.testrar()
    except rarfile.BadRarFile:
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return True
    return False

def delete_corrupted_comics(directory="F:\\Books"):
    """Check and delete corrupted .cbr and .cbz files in the specified directory, ignoring 0 KB files."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:  # Ignore 0 KB files
            if file.lower().endswith(".cbz") and is_zip_corrupted(filepath):
                print(f"Deleting corrupted CBZ file: {filepath}")
                os.remove(filepath)
            elif file.lower().endswith(".cbr") and is_rar_corrupted(filepath):
                print(f"Deleting corrupted CBR file: {filepath}")
                os.remove(filepath)

if __name__ == "__main__":
    delete_corrupted_comics()
    print("Scan complete.")
