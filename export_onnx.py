import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
output_dir = "onnx_model"
os.makedirs(output_dir, exist_ok=True)

print(f"Loading model and tokenizer: {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
base_model = AutoModel.from_pretrained(model_id)
base_model.eval()

print("Saving tokenizer files to onnx_model...")
tokenizer.save_pretrained(output_dir)

class BertONNXWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask, token_type_ids):
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            return_dict=False
        )
        return outputs[0]

wrapper = BertONNXWrapper(base_model)
wrapper.eval()

dummy_text = ["مرحبا بك في منصة المواد الذكية"]
encoded = tokenizer(dummy_text, return_tensors="pt")

input_ids = encoded["input_ids"]
attention_mask = encoded["attention_mask"]
token_type_ids = encoded.get("token_type_ids", torch.zeros_like(input_ids))

input_names = ["input_ids", "attention_mask", "token_type_ids"]
output_names = ["last_hidden_state"]

dynamic_axes = {
    "input_ids": {0: "batch_size", 1: "sequence_length"},
    "attention_mask": {0: "batch_size", 1: "sequence_length"},
    "token_type_ids": {0: "batch_size", 1: "sequence_length"},
    "last_hidden_state": {0: "batch_size", 1: "sequence_length"}
}

onnx_file = os.path.join(output_dir, "model.onnx")
print(f"Exporting model to ONNX: {onnx_file}...")

torch.onnx.export(
    wrapper,
    (input_ids, attention_mask, token_type_ids),
    onnx_file,
    input_names=input_names,
    output_names=output_names,
    dynamic_axes=dynamic_axes,
    opset_version=14,
    do_constant_folding=True
)

print(f"Done! Successfully exported ONNX model to '{output_dir}'.")
