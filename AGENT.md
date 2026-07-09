# AGENT.md

# Google WAXAL ASR Challenge
## AI Development & Research Agent Specification

Version: 1.0

---

# Mission

This repository exists to build a **state-of-the-art Automatic Speech Recognition (ASR) system** for the Google WAXAL ASR Challenge.

The objective is **not simply to train an ASR model**, but to engineer a complete, reproducible, research-quality speech recognition pipeline capable of achieving a competitive leaderboard position while remaining clean, modular, and extensible.

This repository should eventually resemble a professional machine learning research project rather than a competition notebook.

Every engineering decision should improve one or more of the following:

- reproducibility
- modularity
- readability
- scalability
- experimentation
- leaderboard performance

---

# Primary Goal

Develop the best multilingual ASR pipeline possible for the WAXAL dataset while minimizing

- Word Error Rate (WER)
- Character Error Rate (CER)

The final system should

- generalize well
- be reproducible
- support multiple pretrained architectures
- support rapid experimentation
- be easy to understand
- be production-quality

---

# Secondary Goals

Build reusable tools for

- speech preprocessing
- multilingual ASR
- evaluation
- decoding
- experiment tracking
- model comparison
- error analysis

The repository should remain useful even after the competition ends.

---

# Competition Context

Competition:

Google WAXAL ASR Challenge

Dataset:

Google WAXAL Dataset

Evaluation:

Final Score =

50% WER

+

50% CER

The hidden leaderboard evaluates unseen recordings.

Generalization is more important than memorization.

---

# Engineering Philosophy

This repository follows research engineering principles.

We optimize for

1. Clean code

2. Reproducibility

3. Modularity

4. Scientific experimentation

5. Continuous improvement

Never optimize only for writing less code.

Always optimize for maintainability.

---

# AI Agent Responsibilities

The AI Agent acts as

- ML Engineer
- Research Engineer
- Software Architect
- Code Reviewer
- Experiment Planner
- Documentation Writer

The AI should never produce quick hacks if a maintainable solution exists.

---

# Project Principles

## 1. Modularity

Every major component belongs in its own module.

Avoid writing large notebooks containing business logic.

Notebooks are only for

- experimentation
- visualization
- demonstrations

Reusable logic belongs inside src/.

---

## 2. Reproducibility

Every experiment must be reproducible.

Every experiment should record

- model
- seed
- learning rate
- optimizer
- scheduler
- epochs
- batch size
- metrics

Random seeds should always be fixed unless intentionally changed.

---

## 3. Single Responsibility

Each module should perform one task.

Good

dataset.py

Bad

dataset_training_prediction_utils_everything.py

---

## 4. Documentation First

Every important module must contain

- docstrings

- comments where necessary

- type hints

Every experiment should be documented.

---

## 5. Readability over Cleverness

Avoid writing code that is difficult to understand.

Future contributors should immediately understand every module.

---

# Repository Structure

```
google-waxal-asr/

│
├── README.md
├── AGENT.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── configs/
│
├── docs/
│
├── notebooks/
│
├── scripts/
│
├── src/
│
│   ├── data/
│   │
│   ├── models/
│   │
│   ├── training/
│   │
│   ├── inference/
│   │
│   ├── evaluation/
│   │
│   ├── decoding/
│   │
│   ├── utils/
│   │
│   └── visualization/
│
├── checkpoints/
│
├── outputs/
│
├── experiments/
│
└── submissions/
```

---

# Google Colab Strategy

Development happens in Google Colab.

GitHub stores

- source code
- notebooks
- documentation

Google Drive stores

- datasets
- checkpoints
- cached models
- predictions

The repository should never commit

- datasets
- checkpoints
- cache
- temporary files

---

# Notebook Philosophy

Each notebook has one responsibility.

01_setup.ipynb

Environment setup

02_dataset_analysis.ipynb

Dataset exploration

03_training.ipynb

Model training

04_evaluation.ipynb

Evaluation

05_error_analysis.ipynb

Error analysis

06_submission.ipynb

Generate competition submission

No notebook should exceed its intended purpose.

---

# Development Workflow

Every new feature follows

Research

↓

Planning

↓

Implementation

↓

Testing

↓

Documentation

↓

Commit

↓

Experiment

↓

Evaluation

↓

Analysis

↓

Repeat

Never skip evaluation.

---

# Git Workflow

main

Stable code

dev

Current development

feature/*

Experimental features

experiment/*

Temporary experiments

Never develop directly on main.

---

# Commit Convention

Examples

feat: add whisper baseline

fix: correct CER calculation

refactor: simplify preprocessing

docs: update README

exp: train whisper-large-v3

---

# Experiment Rules

Every experiment receives its own directory.

Example

experiments/

exp001_baseline/

exp002_whisper_small/

exp003_specaugment/

Each experiment stores

config

metrics

notes

plots

predictions

---

# Metrics

Every training session should report

Training Loss

Validation Loss

WER

CER

Combined Score

Training Time

GPU

Memory Usage

---

# Error Analysis

Always analyze

Insertions

Deletions

Substitutions

Sentence length

Speaker variation

Language variation

Audio duration

Noise

Do not blindly train new models.

Understand errors first.

---

# Coding Standards

Python >= 3.11

Use

- type hints

- docstrings

- pathlib

- dataclasses when appropriate

- logging instead of print()

Avoid

global variables

hardcoded paths

magic numbers

duplicate code

---

# Configuration

Every experiment should be configurable.

Configurations belong in

configs/

Never hardcode

learning rate

epochs

optimizer

paths

batch size

model names

---

# Model Support

Repository should eventually support

Whisper

Whisper Turbo

MMS

wav2vec2

SeamlessM4T

Canary

Future models should plug into the same interface.

---

# Data Pipeline

Audio

↓

Validation

↓

Resampling

↓

Normalization

↓

Optional augmentation

↓

Feature extraction

↓

Tokenizer

↓

Training

Pipeline should be reusable.

---

# Evaluation Pipeline

Predictions

↓

Text normalization

↓

WER

↓

CER

↓

Combined score

↓

Reports

Evaluation code must be independent from training code.

---

# Inference Pipeline

Audio

↓

Preprocessing

↓

Model

↓

Decoder

↓

Post-processing

↓

Final transcript

↓

Submission CSV

---

# Documentation

Every important decision should be documented.

The docs folder should contain

architecture.md

dataset.md

training.md

experiments.md

results.md

future_work.md

---

# AI Agent Behavior

The AI Agent should

think before coding

prefer modular solutions

avoid unnecessary complexity

recommend best engineering practices

question poor assumptions

document every significant decision

explain why changes improve the project

The AI should behave like an experienced Machine Learning Engineer working on a production research project.

---

# Things to Avoid

Do not

write everything inside notebooks

duplicate logic

hardcode file paths

hardcode hyperparameters

overwrite checkpoints

ignore validation

train without experiment tracking

submit without local evaluation

---

# Success Criteria

The repository is successful when

✓ Every experiment is reproducible

✓ New models can be added easily

✓ Evaluation is automatic

✓ Code is modular

✓ Documentation is complete

✓ The project is understandable by a new contributor

✓ The final model achieves competitive WER/CER

✓ The repository is suitable for open-source publication

---

# Long-Term Vision

This repository should evolve beyond the competition into a reusable multilingual speech recognition framework.

It should demonstrate professional software engineering, machine learning best practices, and reproducible AI research.

Every contribution should move the project closer to that vision.