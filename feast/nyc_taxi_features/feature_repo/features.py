from datetime import timedelta
from feast import Entity, FeatureView, Field, BigQuerySource
from feast.types import Float32, Int64

pickup_zone = Entity(
    name="pickup_location_id",
    description="TLC taxi zone ID for pickup location",
)

zone_stats_source = BigQuerySource(
    name="zone_stats_source",
    table="nyc-taxi-platform-2026.marts.mart_trips_by_zone",
    timestamp_field="trip_timestamp",
)

zone_stats_fv = FeatureView(
    name="zone_daily_stats",
    entities=[pickup_zone],
    ttl=timedelta(days=365),
    schema=[
        Field(name="total_trips", dtype=Int64),
        Field(name="total_revenue", dtype=Float32),
        Field(name="avg_fare", dtype=Float32),
        Field(name="avg_distance", dtype=Float32),
        Field(name="avg_duration_minutes", dtype=Float32),
    ],
    source=zone_stats_source,
)