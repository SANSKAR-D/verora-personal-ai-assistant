nn = 11
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 20)
)

optimizer = nn.SGD(model.parameters(), lr=0.002)