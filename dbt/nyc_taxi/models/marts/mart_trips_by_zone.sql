with trips as (
    select * from {{ ref('int_trips_enriched') }}
)

select
    trip_date,
    timestamp(trip_date) as trip_timestamp,
    pickup_location_id,
    count(*) as total_trips,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(fare_amount), 2) as avg_fare,
    round(avg(trip_distance), 2) as avg_distance,
    round(avg(trip_duration_minutes), 2) as avg_duration_minutes
from trips
group by trip_date, pickup_location_id
order by trip_date, pickup_location_id