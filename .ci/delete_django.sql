-- Making sure the database exists
SELECT * from pg_database where datname = 'django';

-- Disallow new connections
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'django';
ALTER DATABASE django CONNECTION LIMIT 1;

-- Terminate existing connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'django';

-- Drop database
DROP DATABASE django;
