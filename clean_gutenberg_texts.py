import os
import re

# Directory containing downloaded Gutenberg books
INPUT_DIR = "gutenberg_books"

def clean_text(text):
    """
    Removes Project Gutenberg headers, footers, and licensing from a text file.
    """
    start_marker = "*** START OF"
    end_marker = "*** END OF"
    
    lines = text.split("\n")
    inside_book = False
    cleaned_lines = []

    for line in lines:
        if start_marker in line:
            inside_book = True
            continue
        if end_marker in line:
            inside_book = False
            break
        if inside_book:
            cleaned_lines.append(line)

    # Join and clean text
    text = "\n".join(cleaned_lines)
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text

def clean_gutenberg_books():
    """Cleans all text files in the INPUT_DIR by removing Gutenberg headers."""
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(INPUT_DIR, filename)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    text = file.read()

                cleaned_text = clean_text(text)

                # Save cleaned text back to the same file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(cleaned_text)

                print(f"✅ Cleaned: {filename}")
            except Exception as e:
                print(f"❌ Error cleaning {filename}: {e}")

if __name__ == "__main__":
    print("🔄 Cleaning Project Gutenberg text files...")
    clean_gutenberg_books()
    print("🚀 All files cleaned!")
