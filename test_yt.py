from markitdown import MarkItDown
md = MarkItDown()
try:
    res = md.convert("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(res.text_content)
except Exception as e:
    print(f"Exception: {e}")
