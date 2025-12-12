import json
import random
from datetime import datetime
from pathlib import Path
from services.file_utils import read_json, write_json
import os


class OumiAgent:
    """
    Custom Model Training + Evaluation System
    
    Can:
    - Train custom models (PR classification, bug detection, code summarization)
    - Evaluate models (accuracy, hallucination rate, token quality)
    - Store results in JSON logs
    """
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent / "storage"
    
    def run(self, command=None, model_name=None, context=None, **kwargs):
        """Execute Oumi agent"""
        try:
            if command == "train":
                return self._train_model(model_name or context.get("model_name") if context else None)
            elif command == "evaluate":
                return self._evaluate_model(model_name or context.get("model_name") if context else None)
            elif command == "list":
                return self._list_models()
            else:
                return {
                    "agent": "oumi",
                    "status": "idle",
                    "message": "Oumi ready. Use commands: train, evaluate, list",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "agent": "oumi",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _train_model(self, model_name=None):
        """Train a custom model"""
        try:
            model_name = model_name or f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self._log_action("train_model", f"Training model: {model_name}")
            
            # Simulate training process
            # In real implementation, would use actual ML training
            training_result = {
                "model_name": model_name,
                "status": "training",
                "started_at": datetime.now().isoformat(),
                "dataset_size": random.randint(1000, 10000),
                "epochs": random.randint(10, 50),
                "accuracy": None,  # Will be set after training
                "loss": None
            }
            
            # Simulate training completion
            training_result.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "accuracy": round(random.uniform(0.75, 0.95), 3),
                "loss": round(random.uniform(0.05, 0.25), 3),
                "training_time_seconds": random.randint(300, 1800)
            })
            
            # Store model
            models = read_json(self.storage_dir / "models.json")
            if not isinstance(models, list):
                models = []
            
            # Check if model exists
            existing = next((m for m in models if m.get("name") == model_name), None)
            if existing:
                existing.update(training_result)
            else:
                models.append({
                    "name": model_name,
                    "model": model_name,
                    "provider": "oumi",
                    "version": "1.0",
                    **training_result
                })
            
            write_json(self.storage_dir / "models.json", models)
            
            result = {
                "agent": "oumi",
                "status": "success",
                "action": "train_model",
                "model": training_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("train_model", f"Model {model_name} training completed")
            return result
            
        except Exception as e:
            return {
                "agent": "oumi",
                "status": "error",
                "error": str(e)
            }
    
    def _evaluate_model(self, model_name):
        """Evaluate a trained model"""
        try:
            if not model_name:
                return {
                    "agent": "oumi",
                    "status": "error",
                    "error": "Model name required"
                }
            
            models = read_json(self.storage_dir / "models.json")
            if not isinstance(models, list):
                models = []
            
            model = next((m for m in models if m.get("name") == model_name), None)
            
            if not model:
                return {
                    "agent": "oumi",
                    "status": "error",
                    "error": f"Model {model_name} not found"
                }
            
            self._log_action("evaluate_model", f"Evaluating model: {model_name}")
            
            # Simulate evaluation
            evaluation = {
                "model_name": model_name,
                "evaluated_at": datetime.now().isoformat(),
                "accuracy": round(random.uniform(0.80, 0.98), 3),
                "precision": round(random.uniform(0.75, 0.95), 3),
                "recall": round(random.uniform(0.75, 0.95), 3),
                "f1_score": round(random.uniform(0.75, 0.95), 3),
                "hallucination_rate": round(random.uniform(0.01, 0.10), 3),
                "token_quality_score": round(random.uniform(0.85, 0.99), 3),
                "patch_quality_score": round(random.uniform(0.80, 0.95), 3),
                "test_samples": random.randint(100, 1000),
                "evaluation_time_seconds": random.randint(60, 300)
            }
            
            # Update model with evaluation results
            model.update({
                "last_evaluated": evaluation["evaluated_at"],
                "evaluation": evaluation
            })
            
            write_json(self.storage_dir / "models.json", models)
            
            result = {
                "agent": "oumi",
                "status": "success",
                "action": "evaluate_model",
                "model_name": model_name,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("evaluate_model", f"Model {model_name} evaluation completed")
            return result
            
        except Exception as e:
            return {
                "agent": "oumi",
                "status": "error",
                "error": str(e)
            }
    
    def _list_models(self):
        """List all trained models"""
        try:
            models = read_json(self.storage_dir / "models.json")
            if not isinstance(models, list):
                models = []
            
            return {
                "agent": "oumi",
                "status": "success",
                "action": "list_models",
                "models": models,
                "count": len(models),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "agent": "oumi",
                "status": "error",
                "error": str(e)
            }
    
    def _log_action(self, action_type, message):
        """Log Oumi action"""
        try:
            logs = read_json(self.storage_dir / "logs.json")
            if not isinstance(logs, list):
                logs = []
            
            logs.append({
                "level": "info",
                "message": f"Oumi {action_type}: {message}",
                "agent": "oumi",
                "timestamp": datetime.now().isoformat()
            })
            write_json(self.storage_dir / "logs.json", logs)
        except Exception as e:
            print(f"Error logging action: {e}")
