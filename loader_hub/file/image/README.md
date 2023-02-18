# Image Loader

This loader extracts the text from an image that has text in it (e.g. a receipt (key-value pairs) or plain text image). If image has plain text, it uses [pytesseract](https://pypi.org/project/pytesseract/) and If image has for key-value pairs text (Invoice receipts) [Donut](https://huggingface.co/docs/transformers/model_doc/donut) transformer model is used. The file extensions .png, .jpg, and .jpeg are preferred. A single local file is passed in each time you call `load_data`.

## Usage

To use this loader, you need to pass in a `Path` to a local file.

```python
from pathlib import Path
from gpt_index import download_loader

ImageReader = download_loader("ImageReader")

# If the Image has key-value pairs text, use text_type = "key_value"
loader = ImageReader(text_type = "key_value")
documents = loader.load_data(file=Path('./receipt.png'))

# If the Image has plain text, use text_type = "plain_text"
loader = ImageReader(text_type = "plain_text")
documents = loader.load_data(file=Path('./image.png'))
```

This loader is designed to be used as a way to load data into [GPT Index](https://github.com/jerryjliu/gpt_index/tree/main/gpt_index) and/or subsequently used as a Tool in a [LangChain](https://github.com/hwchase17/langchain) Agent. See [here](https://github.com/emptycrown/llama-hub/tree/main) for examples.
