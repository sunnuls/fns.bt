# Инструкция по ручной загрузке модели SVD-XT

## Ссылка на модель
**HuggingFace:** https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt

## Что нужно скачать

Перейдите на страницу: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/tree/main

Вам нужны следующие файлы (~15 GB):

### Основные файлы (ОБЯЗАТЕЛЬНО):
1. **feature_extractor/preprocessor_config.json** (~1 KB)
2. **image_encoder/config.json** (~1 KB)
3. **image_encoder/model.fp16.safetensors** (~1.2 GB) - IMAGE ENCODER
4. **scheduler/scheduler_config.json** (~1 KB)
5. **unet/config.json** (~1 KB)
6. **unet/diffusion_pytorch_model.fp16.safetensors** (~2.9 GB) - UNET
7. **vae/config.json** (~1 KB)
8. **vae/diffusion_pytorch_model.fp16.safetensors** (~10.3 GB) - VAE (самый большой!)
9. **model_index.json** (~1 KB)

## Куда положить файлы

### Вариант 1: В структуру HuggingFace cache (рекомендуется)

Создайте структуру:
```
C:\fns_bot\fanslymotion\cache\models\models--stabilityai--stable-video-diffusion-img2vid-xt\snapshots\9e43909513c6714f1bc78bcb44d96e733cd242aa\
```

И положите туда файлы в таком виде:
```
feature_extractor/
  └── preprocessor_config.json
image_encoder/
  ├── config.json
  └── model.fp16.safetensors
scheduler/
  └── scheduler_config.json
unet/
  ├── config.json
  └── diffusion_pytorch_model.fp16.safetensors
vae/
  ├── config.json
  └── diffusion_pytorch_model.fp16.safetensors
model_index.json
```

### Вариант 2: Прямая структура (проще)

Или просто создайте папку:
```
C:\fns_bot\fanslymotion\models\svd-xt\
```

И положите туда все файлы в той же структуре папок.

## Как скачать

### Способ 1: Через браузер
1. Откройте https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/tree/main
2. Нажмите на каждый файл
3. Нажмите кнопку "download" (стрелка вниз)
4. Сохраните в нужную папку

### Способ 2: Через Git LFS (быстрее)
```bash
# Установите Git LFS если еще нет
git lfs install

# Склонируйте репозиторий
cd C:\fns_bot\fanslymotion\cache\models
git clone https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt
```

### Способ 3: Через wget/curl (Linux/Mac или WSL)
```bash
cd C:\fns_bot\fanslymotion\cache\models
wget -r -np -nH --cut-dirs=1 https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main/
```

## После загрузки

После того как скачаете все файлы, выполните:

```powershell
cd C:\fns_bot\fanslymotion
.\venv\Scripts\python.exe test_model_download.py
```

Это проверит что модель загружается правильно.

## Размеры файлов для проверки

- **image_encoder/model.fp16.safetensors**: ~1.2 GB (1,205 MB)
- **unet/diffusion_pytorch_model.fp16.safetensors**: ~2.9 GB (2,908 MB)  
- **vae/diffusion_pytorch_model.fp16.safetensors**: ~10.3 GB (10,336 MB)
- **Всего**: ~14.4 GB + мелкие config файлы

## Примечание

Если у вас есть доступ к другому компьютеру где модель уже скачана, 
просто скопируйте папку:
```
~/.cache/huggingface/hub/models--stabilityai--stable-video-diffusion-img2vid-xt
```

В папку:
```
C:\fns_bot\fanslymotion\cache\models\
```

