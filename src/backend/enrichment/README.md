# Enrichment Module for Word Sense Disambiguation

This module enhances word disambiguation results by:

1. Cleaning up and organizing data from the basic disambiguation process
2. Using OpenAI's language models to generate:
   - Detailed explanations of each word meaning
   - Example sentences showing contextual usage

## Key Components

### OpenAI Client (`openai_client.py`)

- Handles interactions with the OpenAI API
- Includes fallback mechanism with "dummy" responses if API key isn't available
- Manages error handling and response formatting

### Processor (`processor.py`)

- Cleans up raw disambiguation data for better organization
- Sends prompts to OpenAI to generate rich explanations
- Creates example sentences demonstrating proper usage
- Organizes and structures the enhanced content

## How to Use

### API Integration

The module is integrated into the main FastAPI backend through a dedicated endpoint:

```
POST /api/disambiguate/enriched
```

This endpoint builds on the standard disambiguation process but adds rich AI-generated content to help users understand word meanings in context.

### Environment Configuration

Set up your `.env` file with:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or other available model
```

If you don't provide an API key, the system will fall back to using hardcoded responses to demonstrate functionality.

## Custom Prompts

The module uses carefully crafted prompts to generate:

1. **Detailed Explanations:** 2-3 paragraph educational explanations of word meanings
2. **Example Sentences:** 5 diverse, natural-sounding example sentences for each meaning

## Implementation Notes

- All API calls are asynchronous to prevent blocking the main application
- The module includes comprehensive error handling
- Responses are cached (when possible) to minimize API usage
- Results are logged for debugging and improvement 