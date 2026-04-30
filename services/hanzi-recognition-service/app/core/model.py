import torch
import json
from torchvision import transforms
from PIL import Image
import io
import base64
import torchvision.models as models
import torch.nn as nn
import timm

from app.core.config import settings


class HanziModel:
    def __init__(self):
        self.device = torch.device(settings.device)

        # labels
        with open(settings.labels_path, "r", encoding="utf-8") as f:
            self.labels = json.load(f)

        self.labels = {int(k): v for k, v in self.labels.items()}
        num_classes = len(self.labels)

        self.char_to_id = {v: k for k, v in self.labels.items()}

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
        ])

        self.model = timm.create_model(
            "efficientnet_b0",
            pretrained=False,  # ❗ ważne (zaraz wyjaśnię)
            num_classes=num_classes
        )

        checkpoint = torch.load(settings.model_path, map_location=self.device)

        self.model.load_state_dict(checkpoint["model_state_dict"])

        self.model.to(self.device)
        self.model.eval()

    def build_model(self, num_classes):
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        return model

    def preprocess(self, image_base64: str):
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("L")

        image = self.transform(image)
        image = image.unsqueeze(0)  # batch dim

        return image.to(self.device)

    def predict(self, image_base64: str, topk=5):
        x = self.preprocess(image_base64)

        with torch.no_grad():
            outputs = self.model(x)
            probs = torch.softmax(outputs, dim=1)

        probs, indices = probs.topk(topk, dim=1)

        probs = probs[0].cpu().numpy()
        indices = indices[0].cpu().numpy()

        results = []
        for i in range(topk):
            label_id = int(indices[i])
            results.append({
                "character": self.labels[label_id],
                "confidence": float(probs[i])
            })

        return results
    
    def score_character(self, image_base64: str, character: str, topk=5):
        if character not in self.char_to_id:
            raise ValueError(f"Unknown character: {character}")

        x = self.preprocess(image_base64)

        with torch.no_grad():
            outputs = self.model(x)
            probs = torch.softmax(outputs, dim=1)

        # confidence dla konkretnego znaku
        char_id = self.char_to_id[character]
        confidence = probs[0, char_id].item()

        # top-k (reuse logiki)
        top_probs, top_indices = probs.topk(topk, dim=1)

        top_probs = top_probs[0].cpu().numpy()
        top_indices = top_indices[0].cpu().numpy()

        top_results = []
        for i in range(topk):
            label_id = int(top_indices[i])
            top_results.append({
                "character": self.labels[label_id],
                "confidence": float(top_probs[i])
            })

        return {
            "character": character,
            "confidence": confidence,
            "top_predictions": top_results
        }