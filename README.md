# AI agent for agricultural Operations Classification

## Overview

This tool is designed to process agricultural operation reports and classify them into structured JSON data. It uses a LangGraph-based workflow with YandexGPT as the underlying language model to analyze and extract key information from agricultural operation descriptions.

## Features

- **Operation Segmentation**: Divides input messages into distinct agricultural operations
- **Entity Classification**: Extracts and classifies key entities from each operation
- **JSON Output**: Provides structured JSON output with standardized fields
- **Agricultural Knowledge**: Leverages predefined directories of common operations and crops

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/agricultural-ops-classifier.git
   cd agricultural-ops-classifier
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file with your Yandex Cloud credentials:
     ```
     YC_IAM_TOKEN=your_iam_token
     YC_FOLDER_ID=your_folder_id
     ```

## Usage

```python
from main import compiled_graph

message = """Your agricultural operation report here..."""

result = compiled_graph.invoke({
    "input_message": message,
    "classifyedjson": None,
    "extract_data": None,
    "uncorrect_reason": None,
    "is_correct": None,
    "json_draft": None,
    "messages": []
})

print(result)
```

## Workflow

The tool follows this processing pipeline:
1. **Read Message**: Initial processing of the input text
2. **Divide by Operations**: Splits the message into individual operations
3. **Classify Entities**: Extracts and classifies entities for each operation
4. **Output**: Returns the structured JSON data

## Supported Operations

The tool recognizes a wide range of agricultural operations including:
- Plowing (Пахота)
- Cultivation (Культивация)
- Sowing (Сев)
- Herbicide treatment (Гербицидная обработка)
- And many others...

## Supported Crops

The classification supports numerous crops including:
- Winter wheat (Пшеница озимая)
- Sunflower (Подсолнечник)
- Corn (Кукуруза)
- Soybeans (Соя)
- And many others...

## Output Format

The tool outputs data in this JSON structure:
```json
{
    "date": "Date or null",
    "department": "Department",
    "operation": "Operation name",
    "crop": "Crop name",
    "areaPerDay": "Area per day (ha) or null",
    "totalArea": "Total area (ha) or null",
    "yieldPerDay": "Yield per day (quintals) or null",
    "totalYield": "Total yield (quintals) or null"
}
```

## Requirements

- Python 3.8+
- langchain-core
- langgraph
- yandex-cloud-ml-sdk
- python-dotenv

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

[MIT License](LICENSE)
