# BERT Models Directory

This folder is the designated location for the pre-trained and fine-tuned BERT models.

**Do not check large `.pkl` files into source control.**

When ready, please manually drop the following files into this directory:
- `bert_model.pkl`
- `label_encoder.pkl`
- `tokenizer.pkl`

The `bert_service.py` is already configured to load these files from this exact path (`app/models/bert/`).
