import os
from sentinelhub import (
    SHConfig, SentinelHubStatistical, DataCollection, Geometry, CRS
)
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

# Указываем эндпоинты для Copernicus Data Space (CDSE)
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# ❗️КРИТИЧЕСКИ ВАЖНО: Привязываем коллекцию Sentinel-2 к эндпоинту CDSE
data_collection = DataCollection.SENTINEL2_L2A.define_from(
    "s2_cdse", service_url=config.sh_base_url
)

def get_real_ndvi(geometry_wkt: str, year: int):
    """Возвращает временной ряд NDVI за вегетационный период (май–сентябрь)."""
    # Проверка, что ключи загрузились
    if not config.sh_client_id or not config.sh_client_secret:
        print("❌ ОШИБКА: Ключи SH_CLIENT_ID или SH_CLIENT_SECRET не найдены в .env")
        return []

    try:
        geom = Geometry(geometry_wkt, crs=CRS.WGS84)
        time_interval = (f"{year}-05-01", f"{year}-09-30")

        evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: [{ bands: ["B04", "B08", "dataMask"] }],
            output: [
              { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
              { id: "dataMask", bands: 1 }
            ]
          };
        }
        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          return { ndvi: [ndvi], dataMask: [sample.dataMask] };
        }
        """

        request = SentinelHubStatistical(
            aggregation=SentinelHubStatistical.aggregation(
                evalscript=evalscript,
                time_interval=time_interval,
                aggregation_interval="P10D", # Шаг в 10 дней
                size=[512, 512]
            ),
            input_data=[SentinelHubStatistical.input_data(
                data_collection, # ❗️Используем привязанную коллекцию
                maxcc=0.3
            )],
            geometry=geom,
            config=config
        )

        result = []
        for item in request.get_data():
            for interval in item["data"]:
                date_str = interval["interval"]["from"][:10]
                stats = interval["outputs"]["ndvi"]["bands"]["B0"]["stats"]
                if stats and stats.get("mean") is not None:
                    result.append({
                        "observed_at": date_str,
                        "ndvi": round(float(stats["mean"]), 3)
                    })
        return result
    except Exception as e:
        print(f"❌ Ошибка Sentinel Hub: {e}")
        return []
