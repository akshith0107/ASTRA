import torch
import torch.nn as nn

class BiLSTMModel(nn.Module):
    """
    BiLSTM model matching the architecture of the production model (model(1).pkl).
    vocab_size=1180, embedding_dim=128, hidden_dim=128, output_dim=2, no dropout.
    """
    def __init__(self, vocab_size=1180, embedding_dim=128, hidden_dim=128, output_dim=2, use_dropout=False):
        super(BiLSTMModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )
        # Dropout is optional — original production model has no dropout
        self.use_dropout = use_dropout
        self.dropout = nn.Dropout(0.3) if use_dropout else nn.Identity()
        # Bidirectional: hidden_dim * 2
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)
        output, (hidden, cell) = self.lstm(embedded)
        # Concatenate final forward and backward hidden states
        hidden_cat = torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1)
        return self.fc(self.dropout(hidden_cat))
