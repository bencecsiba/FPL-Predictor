import torch.nn as nn

def fc(in_channels, out_channels):
    return nn.Sequential(
        nn.Linear(in_channels, out_channels), 
        nn.ReLU(),
    )

class fc_model(nn.Module):
    def __init__(self, dropout: float = 0.2):
        
        super().__init__()
        
        self.model = nn.Sequential(
                
            fc(46, 64),
            fc(64, 128),
            fc(128, 256),
            fc(256, 512),
            fc(512, 1024),
            fc(1024, 2048),
            fc(2048, 1024),
            fc(1024, 512),
            fc(512, 444),
            fc(444, 211),
            fc(211, 128),
            fc(128, 96),
            fc(96, 64),
            fc(64, 48),
            fc(48, 24),
            fc(24, 12),
            fc(12, 4),
            fc(4, 1)
        )
    
    def forward(self, x):

        x = self.model(x)
        
        return x
    
