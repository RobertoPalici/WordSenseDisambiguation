"""
Transformer model manager for singleton access to transformer models.

This module provides centralized access to transformer models ensuring they
are only loaded once for better performance and memory usage.
"""

import torch
from transformers import AutoTokenizer, AutoModel
from . import logger

class TransformerModelManager:
    """
    Manages transformer models to ensure they are only loaded once.
    
    Implements the singleton pattern for model and tokenizer instances.
    """
    
    _instance = None
    _models = {}
    _tokenizers = {}
    
    def __new__(cls):
        """Ensure only one instance of the manager exists."""
        if cls._instance is None:
            cls._instance = super(TransformerModelManager, cls).__new__(cls)
            logger.info("Creating new TransformerModelManager instance")
        return cls._instance
    
    def get_model(self, model_name: str) -> AutoModel:
        """
        Get a model instance, loading it if not already loaded.
        
        Args:
            model_name: The HuggingFace model name
            
        Returns:
            The model instance
        """
        if model_name not in self._models:
            logger.info(f"Loading model: {model_name}")
            self._models[model_name] = AutoModel.from_pretrained(model_name)
            logger.info(f"Model {model_name} loaded successfully")
        return self._models[model_name]
    
    def get_tokenizer(self, model_name: str) -> AutoTokenizer:
        """
        Get a tokenizer instance, loading it if not already loaded.
        
        Args:
            model_name: The HuggingFace model name
            
        Returns:
            The tokenizer instance
        """
        if model_name not in self._tokenizers:
            logger.info(f"Loading tokenizer: {model_name}")
            self._tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Tokenizer {model_name} loaded successfully")
        return self._tokenizers[model_name]
    
    def get_embedding(self, text: str, model_name: str) -> torch.Tensor:
        """
        Get embedding for a text using the specified model.
        
        Args:
            text: The text to embed
            model_name: The model to use for embedding
            
        Returns:
            The embedding tensor
        """
        tokenizer = self.get_tokenizer(model_name)
        model = self.get_model(model_name)
        
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Use mean of last hidden state as sentence embedding
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embedding

# Singleton instance to be imported by other modules
model_manager = TransformerModelManager() 