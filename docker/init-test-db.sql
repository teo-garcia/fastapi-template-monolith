SELECT 'CREATE DATABASE fastapi_monolith_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastapi_monolith_test')\gexec
