with trips as (
    select * from {{ ref('int_trips_enriched') }}
)

select
    trip_date,
    count(*) as total_trips,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(fare_amount), 2) as avg_fare,
    round(avg(trip_distance), 2) as avg_distance,
    round(avg(trip_duration_minutes), 2) as avg_duration_minutes,
    round(avg(tip_amount), 2) as avg_tip,
    countif(payment_type = '1') as credit_card_trips,
    countif(payment_type = '2') as cash_trips
from trips
group by trip_date
order by trip_date