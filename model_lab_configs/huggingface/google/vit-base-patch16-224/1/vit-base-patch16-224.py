# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms

from olive.data.registry import Registry


class ViTDataset(Dataset):
    def __init__(self, data):
        self.images = data["images"]
        self.labels = data["labels"]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        return {"input": self.images[idx]}, self.labels[idx]


@Registry.register_post_process()
def dataset_post_process(output):
    return torch.argmax(output, dim=1)


preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


@Registry.register_pre_process()
def dataset_pre_process(output_data, **kwargs):
    size = kwargs.get("size", 256)
    labels = []
    images = []
    for i, sample in enumerate(output_data):
        if i >= size:
            break
        image = sample["image"].convert("RGB")
        image = preprocess(image)
        images.append(image)
        labels.append(sample["label"])

    return ViTDataset({"images": np.array(images), "labels": np.array(labels)})
