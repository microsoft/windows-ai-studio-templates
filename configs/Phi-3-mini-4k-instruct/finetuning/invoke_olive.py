from olive.workflows import run as olive_run
import os
# enable for Wandb integration
# import wandb

# wandb.login()
# Run olive from file for debug.
file_path = os.path.join(os.getcwd(), 'finetuning/olive-config.json')
olive_run(file_path)
