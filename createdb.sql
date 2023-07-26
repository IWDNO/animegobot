create table watching_list(
    id integer primary key,
    anime_name text,
    anime_link text,
    user VARCHAR(255),
    watched integer,
    released_episodes integer,
    total_episodes integer,
    next_episode_date text
);
