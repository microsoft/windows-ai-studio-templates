from typing import (
    Dict, OrderedDict, List, Optional, Tuple, Union,
    TYPE_CHECKING,
)
from dataclasses import dataclass
from random import Random
import torch

from transformers import (
    AutoTokenizer,
    CLIPImageProcessor,
    CLIPTextModelWithProjection,
    CLIPVisionModelWithProjection,
)
from transformers.modeling_outputs import ModelOutput as _ModelOutput

from olive.data.component.dataset import BaseDataset
from olive.data.registry import Registry

if TYPE_CHECKING:
  from datasets import Dataset
  from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast


def load_text_model(model_name):
  @dataclass
  class ModelOutput(_ModelOutput):
    """Wrapper for ModelOutput class from transformers.modeling_outputs.
    Always returns None for missing keys when accessed with __getitem__
    or __getattr__.
    """

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

    def __getitem__(self, k):
      if isinstance(k, str) and k not in self.keys():
        return None
      return super().__getitem__(k)

    def __getattr__(self, k):
      if k in self.keys():
        return self[k]
      return None

  class CLIPTextEncoder(torch.nn.Module):
    def __init__(self, model):
      super().__init__()
      self.embeddings = model.text_model.embeddings
      self.encoder = model.text_model.encoder
      self.final_layer_norm = model.text_model.final_layer_norm
      self.text_projection = model.text_projection

    def forward(
        self,
        input_ids,
        attention_mask,
    ):
      inputs_embeds = self.embeddings(input_ids)
      encoder_outputs = self.encoder(inputs_embeds, attention_mask)
      last_hidden_state = self.final_layer_norm(encoder_outputs[0])

      pooled_output = last_hidden_state[
          torch.arange(last_hidden_state.shape[0]),
          input_ids.argmax(dim=-1),
      ]

      text_embeds = self.text_projection(pooled_output)
      return ModelOutput(
          text_embeds=text_embeds,
          last_hidden_state=last_hidden_state,
      )

  model = CLIPTextModelWithProjection.from_pretrained(model_name).eval()
  return CLIPTextEncoder(model)


def load_vision_model(model_name):
  return CLIPVisionModelWithProjection.from_pretrained(model_name).eval()

@Registry.register_pre_process()
def image_pre_process(
    dataset,
    model_name: str,
    input_col,
    label_col="label",
    max_samples=None,
    shuffle=False,
    seed=42,
    **kwargs,
):
  if max_samples is not None:
    max_samples = min(max_samples, len(dataset))
    dataset = dataset.select(
      Random(seed).sample(range(len(dataset)), max_samples)
      if shuffle
      else range(max_samples)
    )

  processor = CLIPImageProcessor.from_pretrained(model_name)

  tensor_ds = dataset.map(
      lambda sample, indices: {
          "pixel_values": processor(sample[input_col])["pixel_values"],
          label_col: sample.get(label_col, indices),
      },
      batched=True,
      with_indices=True,
      remove_columns=dataset.column_names,
  )
  tensor_ds.set_format("torch", output_all_columns=True)

  return BaseDataset(tensor_ds, label_col=label_col)


@Registry.register_post_process()
def image_post_process(output):
  if isinstance(output, (Dict, OrderedDict)):
    return output["logits"].argmax(dim=-1)
  elif isinstance(output, torch.Tensor):
    return output.argmax(dim=-1)

  raise ValueError(f"Unsupported output type: {type(output)}")


def create_4d_mask(
    mask: torch.Tensor,
    input_shape: Union[torch.Size, Tuple[int, int]],
    masked_value: float = -50.0
) -> torch.Tensor:
  # (batch_size, num_heads, seq_len, head_dim)
  batch_sz, seq_len = input_shape
  expanded_mask = mask[:, None, None, :].expand(
      batch_sz, 1, seq_len, seq_len)
  inverted_mask = 1.0 - expanded_mask.float()
  return inverted_mask.masked_fill(inverted_mask.bool(), masked_value)


def tokenize_hfdataset(
    dataset: "Dataset",
    tokenizer: "Union[PreTrainedTokenizer, PreTrainedTokenizerFast]",
    input_cols: List[str],
    label_col: str = "label",
    seq_length: int = 512,
    max_samples: Optional[int] = None,
):
  def generate_inputs(sample, indices):
    encoded_input = tokenizer(
        [i[0] for i in sample[input_cols[0]]],
        padding="max_length",
        max_length=seq_length,
        truncation=True,
        add_special_tokens=True,
        return_tensors="pt"
    )

    batch_sz = encoded_input.input_ids.shape[0]
    input_ids = encoded_input.input_ids
    attention_mask = create_4d_mask(
        encoded_input.attention_mask,
        (batch_sz, seq_length),
    )
    # position_ids = torch.arange(seq_length).expand(batch_sz, -1)

    return {
      "input_ids": input_ids,
      "attention_mask": attention_mask,
      # "position_ids": position_ids,
      label_col: sample.get(label_col, indices),
    }

  if max_samples is not None and max_samples < len(dataset):
    dataset = dataset.select(range(max_samples))

  tokenized_datasets = dataset.map(
      generate_inputs,
      batched=True,
      with_indices=True,
      remove_columns=dataset.column_names,
  )

  def enforce_dtype(batch):
    batch = {k: torch.Tensor(v) for k, v in batch.items()}
    batch["input_ids"] = batch["input_ids"].int()
    # batch["position_ids"] = batch["position_ids"].int()
    return batch

  tokenized_datasets.set_transform(enforce_dtype)

  return tokenized_datasets


@Registry.register_pre_process()
def tokenize_dataset(
    dataset,
    model_name: str,
    input_cols: List[str],
    max_samples: Optional[int],
    label_col: str = "label",
    seq_length: int = 512,
    **kwargs
):
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  dataset = tokenize_hfdataset(
      dataset, tokenizer, input_cols, label_col=label_col,
      seq_length=seq_length, max_samples=max_samples,
  )
  return BaseDataset(list(dataset), label_col)


@Registry.register_post_process()
def embed_post_process(output):
  if isinstance(output, (Dict, OrderedDict)):
    if "embeds" in output:
      return output["embeds"]
    elif "text_embeds" in output:
      return output["text_embeds"]
    elif "image_embeds" in output:
      return output["image_embeds"]
  elif isinstance(output, torch.Tensor):
    return output.argmax(dim=-1)

  raise ValueError(f"Unsupported output type: {type(output)}")
