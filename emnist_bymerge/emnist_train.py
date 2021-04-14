import argparse
import time
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim
from pytorch_models import networks

# パーサーの設定
parser = argparse.ArgumentParser()
parser.add_argument("net", type=str, help="ネットワークモデルの名前")
parser.add_argument("-e", "--epochs", type=int, default=200, help="学習エポック数")
parser.add_argument("-b", "--batch_size", type=int, default=89, help="学習時のバッチサイズ")
parser.add_argument("-a", "--best_accuracy", type=float, default=0.90817, help="同じモデルの過去の最高精度")
args = parser.parse_args()

# オーグメント設定
normalize = transforms.Normalize(  # データの正規化（各チャネルの平均，各チャネルの標準偏差）
    mean=[0.1307, ],
    std=[0.3081, ],
)
transform_train = transforms.Compose([
    transforms.RandomPerspective(),
    transforms.RandomRotation(10, fill=(0,)),
    transforms.ToTensor(),  # Tensor
    normalize
])
transform_test = transforms.Compose([
    transforms.ToTensor(),  # Tensor
    normalize
])

# 学習データをダウンロード
trainset = torchvision.datasets.EMNIST(root='./data', split='bymerge', train=True, download=True,
                                       transform=transform_train)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=args.batch_size, shuffle=True, num_workers=4)

# テストデータをダウンロード
testset = torchvision.datasets.EMNIST(root='./data', split='bymerge', train=False, download=True,
                                      transform=transform_test)
testloader = torch.utils.data.DataLoader(testset, batch_size=args.batch_size, shuffle=False, num_workers=4)

# デバイスの設定
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"{device} で学習するっぴ！")

# モデルの選択
net = networks.get_net(args.net)
print(net)

# 損失関数
criterion = nn.CrossEntropyLoss()
# 最適化関数
optimizer = optim.Adam(net.parameters(), lr=0.005)

# 学習
print("学習を始めるっぴ！")
epochs = args.epochs
best_acc = args.best_accuracy
bast_epoch = 0
start = time.time()
for epoch in range(1, epochs + 1):
    print("epoch: %d/%d" % (epoch, epochs))
    for phase in ['train', 'test']:
        if phase == 'train':  # 学習
            running_loss = 0.0
            for i, data in enumerate(trainloader, 0):
                # データの取得
                inputs, labels = data[0].to(device), data[1].to(device)
                # 勾配を初期化
                optimizer.zero_grad()
                # 順伝播，逆伝播，パラメータ更新
                outputs = net(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                # loss の出力
                running_loss += loss.item()
                if i % 2000 == 1999:  # iが0からのカウントなので2000イテレーションごと
                    print("iter: %d, loss: %f, time: %ds" % (i + 1, running_loss / 2000, int(time.time() - start)))
                    running_loss = 0.0
        else:  # 評価
            correct = 0
            total = 0
            with torch.no_grad():
                for data in testloader:
                    # データの取得
                    images, labels = data[0].to(device), data[1].to(device)
                    # 順伝播，クラス判定
                    outputs = net(images)
                    _, predicted = torch.max(outputs.data, 1)
                    # 精度算出
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    acc = correct / total
            print(f"Accuracy: {acc}")
            if acc > best_acc:
                # モデルの保存
                best_acc = acc
                bast_epoch = epoch
                weight_path = f"./emnist_weight/{args.net}_bs{args.batch_size}.pth"
                torch.save(net.state_dict(), weight_path)

print("学習が終わったっぴ！")
print(f"一番精度が高い epoch は {bast_epoch} だっぴ！")
