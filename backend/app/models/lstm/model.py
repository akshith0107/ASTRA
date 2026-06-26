import torch
import torch.nn as nn

class BiLSTMModel(nn.Module):
    def __init__(self, vocab_size=1180, embedding_dim=128, hidden_dim=128, output_dim=2):
        super(BiLSTMModel, self).__init__()
        # Ensure identical architectural parameters to align with state_dict
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=1, 
            batch_first=True, 
            bidirectional=True
        )
        # Bidirectional means output from LSTM is hidden_dim * 2
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)
        # output shape: (batch, seq_len, hidden_dim * 2)
        # hidden shape: (num_layers * num_directions, batch, hidden_dim)
        output, (hidden, cell) = self.lstm(embedded)
        
        # Concatenate the final forward and backward hidden states
        # hidden[-2, :, :] is the last forward state
        # hidden[-1, :, :] is the last backward state
        hidden_cat = torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1)
        
        return self.fc(hidden_cat)
