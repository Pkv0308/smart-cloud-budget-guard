create table resources(
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