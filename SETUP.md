# SETUP.md

# Google WAXAL ASR Challenge
## Project Bootstrap Instructions for AI Agents

---

# PURPOSE

You are responsible for setting up this repository as a production-quality AI research environment for the Google WAXAL ASR Challenge.

This is NOT a simple competition repository.

This repository is intended to become a reusable Automatic Speech Recognition (ASR) research framework that can be reused for future competitions and research projects.

You should think and act like a senior Machine Learning Engineer and AI Research Engineer.

Never take shortcuts.

Everything you create should be clean, modular, documented, reproducible and scalable.

---

# PRIMARY OBJECTIVES

Your objectives, in order of importance, are:

1. Build a maintainable repository.
2. Ensure reproducibility.
3. Optimize for AI-assisted development.
4. Organize the repository for long-term research.
5. Keep experiments isolated.
6. Keep documentation synchronized.
7. Make the repository reusable.

Winning the competition is important.

Building a research platform is even more important.

---

# DEVELOPMENT PHILOSOPHY

This project follows the following principles.

## Everything is documented.

Every important decision must be written down.

Never leave undocumented code.

Never leave undocumented experiments.

Never leave undocumented architectural decisions.

---

## Everything is reproducible.

Running the same configuration twice should produce equivalent results.

Use deterministic seeds whenever possible.

Never hardcode paths.

Never hardcode secrets.

Never hardcode hyperparameters.

Everything belongs inside configuration files.

---

## Everything is modular.

Never write giant scripts.

Break everything into reusable modules.

Every module should have one responsibility.

---

## Configuration over code.

Hyperparameters belong inside YAML files.

Never modify Python code just to change training parameters.

---

## Experiment-driven development.

Every change must be associated with an experiment.

Never overwrite previous results.

---

# PROJECT ROOT

The repository should have the following structure.

/
│
├── README.md
├── AGENTS.md
├── SETUP.md
├── ROADMAP.md
├── PROJECT_RULES.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
│
├── .gitignore
├── .editorconfig
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
│
├── .github/
│
├── .opencode/
│
├── configs/
│
├── data/
│
├── docs/
│
├── experiments/
│
├── notebooks/
│
├── outputs/
│
├── scripts/
│
├── src/
│
├── submissions/
│
└── tests/

This structure should remain stable throughout the project.

---

# OPENCODE CONFIGURATION

Create the following structure.

.opencode/

    agents/

    skills/

    prompts/

    memory/

    templates/

    opencode.json

The AI should use this directory as its working environment.

Never place project code inside .opencode.

Only AI resources belong there.

---

# AGENTS

Create specialized agents.

Do NOT create one giant agent.

Each agent should have a single responsibility.

Recommended agents:

planner

researcher

dataset-engineer

preprocessing

training

evaluation

submission

reviewer

documentation

experiment-manager

github

strategist

Every agent should contain:

- clear purpose
- responsibilities
- constraints
- allowed tools
- preferred workflow
- output format

---

# SKILLS

Create reusable skills.

Every skill should solve one specific problem.

Examples:

audio-loading

dataset-analysis

feature-extraction

augmentation

specaugment

noise

speed-perturbation

whisper

wav2vec

xlsr

huggingface

wer

cer

experiment-tracking

logging

github

python

colab

zindi

Each skill must contain:

Purpose

Inputs

Outputs

Best practices

Common mistakes

Examples

References

Never combine unrelated skills.

---

# MEMORY

Create persistent project memory.

memory/

competition.md

dataset.md

papers.md

ideas.md

mistakes.md

leaderboard.md

models.md

experiments.md

These files are continuously updated.

Never delete information.

Append instead.

---

# DOCUMENTATION

Maintain documentation continuously.

Required files:

README.md

ARCHITECTURE.md

MODELS.md

TRAINING.md

DATASET.md

SUBMISSIONS.md

CHANGELOG.md

ROADMAP.md

PROJECT_RULES.md

Documentation is part of development.

Never postpone documentation.

---

# SOURCE CODE

All production code belongs inside

src/

Organize into packages.

Example

src/

data/

models/

training/

evaluation/

metrics/

utils/

config/

pipeline/

Never place reusable code inside notebooks.

---

# NOTEBOOKS

Jupyter notebooks are for:

EDA

Visualization

Quick experiments

Debugging

Nothing else.

If notebook code becomes useful,

move it into src/.

---

# CONFIGURATION

Use YAML.

configs/

baseline.yaml

whisper-small.yaml

whisper-medium.yaml

large-v3.yaml

augmentation.yaml

evaluation.yaml

inference.yaml

Never duplicate configuration.

Use inheritance if possible.

---

# EXPERIMENTS

Every experiment gets its own folder.

Example

experiments/

001_baseline/

002_whisper_small/

003_specaugment/

Each experiment contains

config.yaml

metrics.json

notes.md

logs/

plots/

predictions.csv

checkpoint.md

Never overwrite experiments.

---

# DATA

Keep data organized.

data/

raw/

processed/

interim/

external/

metadata/

Never edit raw data.

Raw data is immutable.

---

# OUTPUTS

outputs/

models/

logs/

figures/

predictions/

temporary/

Automatically create missing directories.

---

# SUBMISSIONS

Store every submission.

submissions/

submission_001.csv

submission_002.csv

submission_003.csv

Also include

notes.md

describing:

model

WER

configuration

date

---

# TESTS

Create unit tests.

Test

metrics

preprocessing

loading

evaluation

configuration

No production code without tests.

---

# GITHUB

Create

.github/

workflows/

Issue templates

PR template

CODEOWNERS

Dependabot

GitHub Actions

CI should check

formatting

linting

unit tests

---

# CODING STANDARDS

Python

PEP8

Type hints

Docstrings

Meaningful variable names

Small functions

Reusable modules

No duplicated code

No global variables

No magic numbers

---

# LOGGING

Use structured logging.

Every important event should be logged.

Training

Evaluation

Inference

Checkpoint saving

Experiment creation

Submission generation

---

# ERROR HANDLING

Never silently ignore errors.

Raise meaningful exceptions.

Provide actionable messages.

Log failures.

---

# VERSION CONTROL

Commit often.

Use meaningful commit messages.

Examples

feat(training): add Whisper baseline

fix(metrics): correct WER computation

docs: update architecture

refactor(preprocessing): simplify pipeline

---

# AI BEHAVIOR

Before writing code:

Understand the task.

Search the repository.

Reuse existing modules.

Avoid duplication.

Think before coding.

After coding:

Run tests.

Update documentation.

Update changelog.

Update experiments.

Commit changes.

---

# RESEARCH WORKFLOW

Every feature follows

Research

↓

Planning

↓

Implementation

↓

Training

↓

Evaluation

↓

Documentation

↓

Experiment Logging

↓

Submission

Never skip steps.

---

# PERFORMANCE

Prioritize

Readability

Correctness

Reproducibility

Maintainability

Performance

In that order.

---

# WHAT NOT TO DO

Do not create giant scripts.

Do not duplicate code.

Do not hardcode paths.

Do not hardcode hyperparameters.

Do not leave TODOs unresolved.

Do not ignore documentation.

Do not overwrite experiments.

Do not delete research notes.

Do not write notebook-only solutions.

Do not optimize prematurely.

---

# SUCCESS CRITERIA

The setup is complete when:

✓ Repository structure exists

✓ Documentation exists

✓ Agents exist

✓ Skills exist

✓ Memory exists

✓ Config system exists

✓ Source code structure exists

✓ Experiment system exists

✓ GitHub automation exists

✓ Development standards are documented

✓ Repository is ready for implementation

After setup is complete, development of the ASR system may begin.

Until then, focus only on creating the development environment.

This setup document is the single source of truth for repository initialization.
