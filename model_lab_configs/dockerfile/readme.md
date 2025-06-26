- Navigate to `model_lab_configs`

- Build image for QNN and AMD:
```
docker build -f .\dockerfile\qnn\Dockerfile -t {image_tag} .
```

- Build image for Intel:
```
docker build -f .\dockerfile\intel\Dockerfile -t {image_tag} .
```