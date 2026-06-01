import pandas as pd
from datetime import datetime
from feast import FeatureStore

store = FeatureStore(repo_path=".")

entity_df = pd.DataFrame({
    "pickup_location_id": [132, 161, 237, 186, 79],
    "trip_timestamp": [
        datetime(2022, 6, 1),
        datetime(2022, 6, 1),
        datetime(2022, 6, 1),
        datetime(2022, 6, 1),
        datetime(2022, 6, 1),
    ]
})

print("Fetching historical features from offline store...")
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "zone_daily_stats:total_trips",
        "zone_daily_stats:total_revenue",
        "zone_daily_stats:avg_fare",
        "zone_daily_stats:avg_distance",
        "zone_daily_stats:avg_duration_minutes",
    ]
).to_df()

print(training_df)
print()

print("Fetching online features from online store...")
online_features = store.get_online_features(
    features=[
        "zone_daily_stats:total_trips",
        "zone_daily_stats:total_revenue",
        "zone_daily_stats:avg_fare",
    ],
    entity_rows=[
        {"pickup_location_id": 132},
        {"pickup_location_id": 161},
    ]
).to_df()

print(online_features)