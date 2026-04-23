# LearnHanzi-Server

Monorepo backendu projektu LearnHanzi.

## Aktualna struktura
- `services/auth-service` - mikroserwis autentykacji
- `services/hanzi-recognition-service` - mikroserwis identyfikujący hanzi

## Konfiguracja związana z serwisem hanzi-recognition-service 
### Obsługa dużych plików (git lfs) 
Z powodu, że plik modelu przekracza rozmiar plików obsługiwanych przez GitHub, został on dodany przy użyciu git large file system.  
Aby poprawnie pobrać repozytorium wraz z modelem, należy zainstalować Git LFS:  
```git lfs install```
Klonowanie repozytorium:  
```git clone https://github.com/Jakub-Rudnik/LearnHanzi-Server.git```  
Po sklonowaniu repozytorium należy pobrać pliki zarządzane przez Git LFS:  
```git lfs pull```  
Po wykonaniu powyższych kroków należy upewnić się, że plik modelu został poprawnie pobrany:  
```services/hanzi-recognition-service/app/models/hanzi_model.pt```  
### Wirtualne środowisko  
Mikroserwis identyfikujący hanzi posiada odrębnego `.env`. W `ervices/hanzi-recognition-service` znajduje się `.env.example`, który należy skopiować.  

## Założenia
- FastAPI
- PostgreSQL
- Docker Compose
