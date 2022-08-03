Steps to build the app image; (It's already built and pushed to my docker hub account, please pull it from there)

```bash
python3 -m venv k8_exp_env
source k8_exp_env/bin/activate
pip install -r requirements.txt

docker build -f Dockerfile -t mongo-crud-app .
docker tag mongo-crud-app pranavpawar3/mongo_crud_app:v0.0.3
docker push pranavpawar3/mongo_crud_app:v0.0.3
```

