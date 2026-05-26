# LearnHanzi-Server

Monorepo backendu projektu LearnHanzi.

## Aktualna struktura
- `services/auth-service` - mikroserwis autentykacji
- `services/hanzi-recognition-service` - mikroserwis identyfikujący hanzi

## Konfiguracja związana z serwisem hanzi-recognition-service 
### Dodanie pliku zawierającego wytrenowany model
Z powodu, że plik modelu przekracza rozmiar plików obsługiwanych przez GitHub, należy pobrać go z [google drive](https://drive.google.com/file/d/1DpOwfYCmrTQJMlubpwBvHoWpgwmB4aH8/view?usp=sharing) i umieścić w odpowiednim folderze:  
```services/hanzi-recognition-service/app/models/hanzi_model.pt```  

## Utworzenie plików .env
```cp infra/.env.example infra/.env```\
```cp services/auth-service/.env.example services/auth-service/.env```\
```cp services/dictionary-service/.env.example services/dictionary-service/.env```\
```cp services/hanzi-recognition-service/.env.example services/hanzi-recognition-service/.env```\
```cp services/progress-service/.env.example services/progress-service/.env```

## Wypełnienie tabeli hanzi
Po uruchomieniu kontenera należy wykonać
```docker compose exec dictionary python -m scripts.seed_hanzi```

## Założenia
- FastAPI
- PostgreSQL
- Docker Compose
