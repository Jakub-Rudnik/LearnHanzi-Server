# LearnHanzi-Server

Monorepo backendu projektu LearnHanzi.

## Aktualna struktura
- `services/auth-service` - mikroserwis autentykacji
- `services/hanzi-recognition-service` - mikroserwis identyfikujący hanzi

## Konfiguracja związana z serwisem hanzi-recognition-service 
### Dodanie pliku zawierającego wytrenowany model
Z powodu, że plik modelu przekracza rozmiar plików obsługiwanych przez GitHub, należy pobrać go z [google drive](https://drive.google.com/file/d/1DpOwfYCmrTQJMlubpwBvHoWpgwmB4aH8/view?usp=sharing) i umieścić w odpowiednim folderze:  
```services/hanzi-recognition-service/app/models/hanzi_model.pt```  
### Wirtualne środowisko  
Mikroserwis identyfikujący hanzi posiada odrębnego `.env`. W `ervices/hanzi-recognition-service` znajduje się `.env.example`, który należy skopiować.  

## Założenia
- FastAPI
- PostgreSQL
- Docker Compose
