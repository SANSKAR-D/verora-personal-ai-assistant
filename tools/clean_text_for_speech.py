import re

def clean_text_for_speech(text: str) -> str:
    """Strips markdown and symbols that shouldn't be spoken aloud."""
    # Strip ALL non-ASCII characters that Piper/eSpeak can't phonemize
    # (surrogates like \udc8f, arrows ↑→, currency ₹, emojis, etc.)
    text = text.encode('ascii', errors='ignore').decode('ascii')

    # Strip emoji and symbol characters entirely
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF" 
        "\U00002600-\U000027BF" 
        "\U0001F1E6-\U0001F1FF" 
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    # Remove bold/italic markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    # Remove markdown headers (#, ##, etc.)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove code blocks and inline code backticks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # Remove markdown links, keep the link text
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)

    # Remove bullet/list markers at line starts
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)

    # Collapse multiple newlines/spaces into single spaces (natural speech flow)
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()