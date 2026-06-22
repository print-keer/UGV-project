# Dataset Notes

This directory will hold the binary threat-classification dataset for the UGV
project.

Expected classes:

- `harmful`
- `harmless`

Recommended structure:

```text
ai/dataset/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── data.yaml
```

The `data.yaml.example` file in this directory is the starting template for the
YOLOv8 training configuration.

## Included dataset integration

The project now supports the extracted `MVRSD_dataset` archive under:

```text
ai/dataset/raw/MVRSD_dataset/data
```

That dataset provides:

- `2400` training images
- `600` validation images
- YOLO label files
- vehicle classes: `SMV`, `LMV`, `AFV`, `CV`, `MCV`

Two training paths are supported:

1. `ai/dataset/mvrsd_multiclass.yaml`
   Keeps the original five vehicle classes.
2. `ai/dataset/processed/mvrsd_binary/data.yaml`
   Collapses all MVRSD vehicle classes into a single `harmful` class for the
   current UGV threat pipeline.
