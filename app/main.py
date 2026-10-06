from fastapi import FastAPI

app = FastAPI(
    title="ДЭ 2026 API",
    description="Информационная система для демонстрационного экзамена",
    version="1.0.0",
)

TRANSFER_SIMULATOR_URL = (
    "http://192.168.1.200:4444/TransferSimulator"
)


@app.get("/")
def root():
    return {
        "message": "ДЭ 2026 API работает"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/config")
def config():
    return {
        "transfer_simulator": TRANSFER_SIMULATOR_URL
    }