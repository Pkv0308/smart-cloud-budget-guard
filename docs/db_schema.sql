create table if not exists resources(
    id serial primary key,
    vm_name varchar(255) not null,
    location varchar(100),
    power_state varchar(50),
    environment varchar(100),
    owner varchar(100),
    project varchar(100),
    tags JSONB,
    last_synced_at timestamp default now(),
    unique (vm_name)
);

create table if not exists vm_metrics(
    id serial primary key,
    vm_name varchar(255) not null references resources(vm_name),
    cpu_percent numeric(5,2),
    network_in_bytes BIGINT,
    network_out_bytes BIGINT,
    recorded_at timestamp default now()
);

-- -- storing VM Azure resouce id for persisting monitoring data

-- alter table resources add column resource_id varchar(500);