# はじめかた

```
# aws-cli のダミー設定
$ aws configure
AWS Access Key ID [None]: dummy
AWS Secret Access Key [None]: dummy
Default region name [None]: ap-northeast-1
Default output format [None]: json

# python の仮想環境設定
$ python -m venv .venv
$ source .venv/bin/activate

## windowsの場合　
$ source .venv/Scripts/activate

$ pip install -r requirements.txt

# serverless framework の設定
$ npm install -g serverless --save-dev

## nodenv を利用している場合
$ nodenv rehash

$ serverless --version

$ serverless plugin install --name serverless-dynamodb
$ serverless plugin install --name serverless-offline

$ serverless dynamodb install
$ serverless dynamodb start
$ serverless offline

# dynamodb のテーブルをGUI上で確認したい場合
$ npx dynamodb-admin

```
